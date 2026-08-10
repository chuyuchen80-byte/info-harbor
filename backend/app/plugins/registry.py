"""插件注册表：入口点发现 + 配置装配（§6.1 / §6.2）。

MVP 阶段先约定 Adapter 抽象；V2 用 importlib.metadata 入口点发现 + pluggy hook。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SourcePlugin(ABC):
    """数据源 Adapter 抽象：新增源实现三个方法 + 注册进 config/sources/，零核心侵入。"""

    key: str  # 唯一标识，对应 Source.adapter_key
    source_type: str = "rss"  # rss / api / static / rendered / manual

    @abstractmethod
    def list_items(self, **kwargs: Any) -> list[dict]:
        """条目列表（标题/URL/发布时间等最小字段，供快速去重）。"""

    @abstractmethod
    def fetch_detail(self, url: str, **kwargs: Any) -> dict:
        """抓取详情（正文精提取由管道层负责，此处只拿原始内容）。"""

    @abstractmethod
    def normalize(self, raw: dict, **kwargs: Any) -> dict:
        """归一化为统一 Article 契约（§7）。"""


class Registry:
    """源注册表：从 config/sources/ 加载并实例化 Adapter。"""

    def __init__(self) -> None:
        self._sources: dict[str, SourcePlugin] = {}

    def register(self, plugin: SourcePlugin) -> None:
        self._sources[plugin.key] = plugin
