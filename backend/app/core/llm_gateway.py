"""统一 LLM 网关（§6.3）：Provider 抽象 / 分级路由 / 缓存 / 预算 / 降级。

MVP：仅落接口占位；V2 全面接入。新增 Provider = 实现三个方法 + 配置注册，业务代码无感。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """LLM Provider 抽象：chat / completion / embed 三方法。"""

    name: str

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """多轮对话补全。"""

    @abstractmethod
    async def completion(self, prompt: str, **kwargs: Any) -> str:
        """单轮补全。"""

    @abstractmethod
    async def embed(self, text: str, **kwargs: Any) -> list[float]:
        """向量化。"""


class LLMGateway:
    """按 task_router.yaml 分级路由，带三级缓存 + 降级链（V2 实现）。"""

    def __init__(self) -> None:
        self._providers: dict[str, BaseLLMProvider] = {}

    def register(self, provider: BaseLLMProvider) -> None:
        self._providers[provider.name] = provider
