"""InfoQ 中文站（infoq.cn）JSON 接口适配器（首批源，接口事实来自实测与用户数据源规划）。

接口形态（公开接口，2026-09 实测，决策见 DECISIONS.md D10）：
- 列表：``POST /public/v1/article/getList``
  body ``{"type":1,"ptype":0,"size":20,"id":<频道ID>,"score":""}``；
  data[] 关键字段：uuid / score（毫秒级游标，末条作下页入参）/ article_title /
  article_summary / publish_time（毫秒时间戳）
- 详情：``POST /public/v1/article/getDetail`` body ``{"uuid":...}``
  元数据（author[].nickname / publish_time / ai_summary）；
  **content 字段已不再直出**，content_url 签名链接 403——
  正文改为抓文章页 HTML 后用 trafilatura 提取，失败回退 ai_summary / article_summary。
"""

from __future__ import annotations

import uuid as uuid_lib
from datetime import UTC, datetime
from typing import Any

import httpx
import trafilatura
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.models import Article, Source
from app.plugins.registry import SourcePlugin

_BASE = "https://www.infoq.cn"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": f"{_BASE}/",
}


def _ms_to_datetime(ms: Any) -> datetime | None:
    """InfoQ 时间字段为毫秒级时间戳；缺失/异常返回 None（契约字段可空）。"""
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=UTC)
    except (TypeError, ValueError, OSError):
        return None


class InfoQSourcePlugin(SourcePlugin):
    """InfoQ JSON 接口适配器：12 个频道由 source.config.channels 驱动。"""

    key = "infoq"
    source_type = "api"  # JSON 接口型（非 RSS）

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    # ---- HTTP（tenacity 重试：网络抖动/偶发失败共尝试 3 次） ----

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    async def _post_json(
        self, client: httpx.AsyncClient, path: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        resp = await client.post(f"{_BASE}{path}", json=payload)
        resp.raise_for_status()
        body = resp.json()
        if body.get("code") != 0:  # InfoQ 业务码：0 = 成功
            raise RuntimeError(f"InfoQ 业务错误 code={body.get('code')} error={body.get('error')}")
        return body

    # ---- SourcePlugin 三方法 ----

    async def list_items(self, source: Source, **kwargs: Any) -> list[dict[str, Any]]:
        """逐频道游标翻页；每频道限 max_pages_per_channel 页，item 附带频道与规范 url。"""
        cfg = source.config or {}
        channels = cfg.get("channels") or []
        max_pages = int(cfg.get("max_pages_per_channel", 2))
        page_size = int(cfg.get("page_size", 20))

        items: list[dict[str, Any]] = []
        async with httpx.AsyncClient(headers=_HEADERS, timeout=self._timeout) as client:
            for channel in channels:
                cursor = ""
                for _ in range(max_pages):
                    body = await self._post_json(
                        client,
                        "/public/v1/article/getList",
                        {
                            "type": 1,
                            "ptype": 0,
                            "size": page_size,
                            "id": channel.get("channel_id"),
                            "score": cursor,
                        },
                    )
                    data = body.get("data") or []
                    if not data:
                        break
                    for raw in data:
                        items.append(
                            {
                                **raw,
                                "url": f"{_BASE}/article/{raw.get('uuid', '')}",
                                "title": raw.get("article_title") or raw.get("article_sharetitle") or "",
                                "_channel": channel,
                            }
                        )
                    cursor = data[-1].get("score") or ""
                    if not cursor:  # 无游标即无下一页
                        break
        return items

    async def fetch_detail(self, item: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """详情元数据 + 正文：正文从文章页 HTML 提取，任何一步失败都不阻断（normalize 有兜底）。"""
        article_uuid = item.get("uuid") or ""
        meta: dict[str, Any] = {}
        content_text = ""
        async with httpx.AsyncClient(
            headers=_HEADERS, timeout=self._timeout, follow_redirects=True
        ) as client:
            try:
                body = await self._post_json(
                    client, "/public/v1/article/getDetail", {"uuid": article_uuid}
                )
                meta = body.get("data") or {}
            except Exception:
                meta = {}
            try:
                resp = await client.get(f"{_BASE}/article/{article_uuid}")
                resp.raise_for_status()
                content_text = (
                    trafilatura.extract(resp.text, favor_recall=True, include_comments=False)
                    or ""
                )
            except Exception:
                content_text = ""
        return {**meta, "_content_text": content_text}

    def normalize(
        self, item: dict[str, Any], detail: dict[str, Any] | None = None, **kwargs: Any
    ) -> Article:
        """归一化为 Article 契约；source 契约经 kwargs 传入（取 id / country）。"""
        source: Source | None = kwargs.get("source")
        detail = detail or {}
        authors = detail.get("author") or []
        author = authors[0].get("nickname") if isinstance(authors, list) and authors else None
        channel = item.get("_channel") or {}
        summary = item.get("article_summary") or detail.get("article_summary") or ""
        content = detail.get("_content_text") or detail.get("ai_summary") or summary

        return Article(
            id=uuid_lib.uuid4().hex,
            source_id=source.id if source else "",
            title=item.get("title") or "",
            url=item.get("url") or "",
            content=content or None,
            summary=summary or None,
            author=author,
            published_at=_ms_to_datetime(
                detail.get("publish_time") or item.get("publish_time")
            ),
            detected_lang="zh",
            country=source.country if source else None,
            source_type=self.source_type,
            tags=[channel["name"]] if channel.get("name") else [],
            ext_json={
                "channel_id": channel.get("channel_id"),
                "channel": channel.get("name"),
                "infoq_aid": item.get("aid"),
            },
        )
