"""去重协调（单一权威，§4-⑧ / §6.2）。

四层去重的职责归属与顺序在此单一权威定义，各层不得各自为战：

  1. URL 布隆过滤器     —— 采集层，入口拦截（RedisBloom）
  2. SimHash + 标题模糊  —— 清洗层（datasketch + rapidfuzz）
  3. embedding 语义去重  —— AI 层，异步离线（cosine 阈值 0.92）

MVP 阶段先落第 1、2 层；第 3 层放 V2。
"""

from __future__ import annotations

from enum import IntEnum


class DedupLayer(IntEnum):
    URL_BLOOM = 1
    SIMHASH_TITLE = 2
    EMBEDDING = 3


# 各层默认阈值（后续移入 YAML 配置）
DEFAULTS: dict[DedupLayer, dict] = {
    DedupLayer.URL_BLOOM: {"enabled": True},
    DedupLayer.SIMHASH_TITLE: {"simhash_bits": 64, "hamming_threshold": 4, "title_ratio": 0.9},
    DedupLayer.EMBEDDING: {"enabled": False, "cosine_threshold": 0.92},  # V2 开启
}


class DedupCoordinator:
    """按固定顺序执行已启用的去重层，返回命中的层（None 表示新内容）。"""

    def __init__(self) -> None:
        self._layers: list[DedupLayer] = [
            layer for layer in DedupLayer if DEFAULTS[layer].get("enabled", True)
        ]

    async def is_duplicate(
        self, url: str, title: str, content: str | None = None
    ) -> tuple[bool, DedupLayer | None]:
        """TODO(MVP)：接入 RedisBloom（URL）与 SimHash（标题）。当前骨架放行全部内容。"""
        return False, None
