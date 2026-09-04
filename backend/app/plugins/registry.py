"""插件注册表：入口点发现 + 配置装配（§6.1 / §6.2）。

M1（爬虫系统）落地：抽象方法 async 化——list_items / fetch_detail 都是网络 IO，
与全异步栈一致。V2 再引入 importlib.metadata 入口点发现 + pluggy hook。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.models import Article, Source


class SourcePlugin(ABC):
    """数据源 Adapter 抽象：新增源实现三个方法 + 注册进 config/sources/，零核心侵入。

    约定：三个方法都以 ``Source`` 契约为输入，插件自行解读 ``source.config``
    （feed_url / 频道列表等源私有配置）；核心不认具体实现，只认这里的方法签名。
    """

    key: str  # 唯一标识，对应 Source.adapter_key
    source_type: str = "rss"  # rss / api / static / rendered / manual

    @abstractmethod
    async def list_items(self, source: Source, **kwargs: Any) -> list[dict[str, Any]]:
        """条目列表：原始 item dict，至少含 url / title；源私有字段（游标、uuid 等）原样保留。"""

    @abstractmethod
    async def fetch_detail(self, item: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """抓取详情：返回 detail dict（原始/半加工均可）；无详情阶段的源返回 {} 即可。"""

    @abstractmethod
    def normalize(
        self, item: dict[str, Any], detail: dict[str, Any] | None = None, **kwargs: Any
    ) -> Article:
        """归一化为统一 Article 契约（§7）。source 契约经 kwargs 传入（取 id/country）。"""


class Registry:
    """源注册表：进程内登记可用 Adapter，按 adapter_key 取用。"""

    def __init__(self) -> None:
        self._sources: dict[str, SourcePlugin] = {}

    def register(self, plugin: SourcePlugin) -> None:
        self._sources[plugin.key] = plugin

    def get(self, key: str) -> SourcePlugin | None:
        return self._sources.get(key)

    def all(self) -> list[SourcePlugin]:
        return list(self._sources.values())
