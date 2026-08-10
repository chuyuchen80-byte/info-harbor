"""领域事件总线（§3 / §4-②）。

事件 schema 在此集中注册，是各层解耦的单一通道，禁止各域另建一份。
MVP 用 in-process 分发；多 worker 后切换 Redis Streams（只换 EventBus 实现）。

主数据流事件链路：
  raw → cleaned → translated → screened → scored → ready
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Awaitable, Callable

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DomainEvent(BaseModel):
    """所有领域事件的基类。"""

    aggregate_id: str
    occurred_at: datetime = Field(default_factory=_utcnow)
    version: int = 1

    @property
    def event_type(self) -> str:
        """默认以类名作为事件类型，便于注册表映射与可观测性。"""
        return self.__class__.__name__


# ---- 主数据流事件 ----

class ArticleRawIngested(DomainEvent):
    """采集层完成：原始快照已存 MinIO，粗结构化进入清洗。"""

    article_id: str
    source_id: str
    raw_snapshot_key: str | None = None


class ArticleCleaned(DomainEvent):
    article_id: str
    source_id: str


class ArticleTranslated(DomainEvent):
    article_id: str
    target_lang: str = "zh"


class ArticleRuleScreened(DomainEvent):
    article_id: str
    rule_score: int
    passed: bool


class ArticleScored(DomainEvent):
    article_id: str
    value_score: float
    llm_model: str | None = None


class ArticleReady(DomainEvent):
    article_id: str


# ---- 事件总线 ----

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """in-process 事件总线：注册 + 异步分发。后期切换 Redis Streams。"""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}

    def register(
        self, event_type: type[DomainEvent]
    ) -> Callable[[EventHandler], EventHandler]:
        """用作装饰器：``@bus.register(ArticleReady)``"""

        def decorator(handler: EventHandler) -> EventHandler:
            self._handlers.setdefault(event_type, []).append(handler)
            return handler

        return decorator

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), ()):
            await handler(event)


def register_domain_events(bus: EventBus) -> None:
    """集中装配：各域的 handler 从这里注册（域实现后填充）。"""
    # 例如：
    #   from app.domain.articles import register as register_articles
    #   register_articles(bus)
