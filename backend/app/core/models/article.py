"""统一数据契约（§7）：Article / Source / Score 的 Pydantic v2 定义。

MVP 先落这三个核心模型；后续扩展（Cluster / Task 等）同样在此单一权威维护。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Entity(BaseModel):
    type: str  # country / company / person / organization ...
    name: str
    confidence: float | None = None


class Article(BaseModel):
    """统一文章契约：从 raw 到 ready 的全链路状态（§7）。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    title: str
    url: str
    raw_url: str | None = None
    content: str | None = None
    summary: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    detected_lang: str | None = None
    translated_lang: str | None = None
    content_translated: str | None = None
    country: str | None = None
    source_type: str = "rss"  # rss / api / static / rendered / manual
    tags: list[str] = Field(default_factory=list)
    entities: list[Entity] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    cluster_id: str | None = None
    raw_snapshot_key: str | None = None
    status: str = "raw"
    ext_json: dict[str, Any] = Field(default_factory=dict)  # 数据源自定义扩展，不改表结构


class Source(BaseModel):
    """源注册表（§8 sources 表）。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country: str | None = None
    type: str = "media"  # media / arxiv / github / hf / government / community / cn_media
    adapter_key: str
    config: dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
    enabled: bool = True
    health: dict[str, Any] = Field(default_factory=dict)


class SourceUpdate(BaseModel):
    """源更新请求体（PATCH 部分更新：只改给出的字段）。"""

    enabled: bool | None = None
    weight: float | None = None


class Score(BaseModel):
    """统一评分契约（§4-⑦）：rule_score + LLM 四维分各自持久化，value_score 权重合成。"""

    article_id: str
    rule_score: int | None = None  # 0-100
    relevance: int | None = None  # 0-10
    timeliness: int | None = None  # 0-10
    impact: int | None = None  # 0-10
    credibility: int | None = None  # 0-10
    llm_model: str | None = None
    confidence: float | None = None
    value_score: float | None = None  # 0-100
    dimension_weights: dict[str, float] = Field(default_factory=dict)
