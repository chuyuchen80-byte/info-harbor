"""文章域持久化模型（SQLAlchemy 2.0 async，映射 §8 的 articles 表）。

字段对齐 `core/models/article.py: Article` 契约。MVP 用 ``url`` 唯一索引做去重，
抓取落库时 ``INSERT ... ON CONFLICT (url) DO NOTHING`` 原子去重（决策 D5）。
JSON 字段用通用 JSON 类型（MySQL 8 / PG 通用）。
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("sources.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    # url 唯一索引做去重：utf8mb4 下 767 字节上限，故限定长度为 512
    url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    raw_url: Mapped[str | None] = mapped_column(String(512))
    content: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    detected_lang: Mapped[str | None] = mapped_column(String(8))
    translated_lang: Mapped[str | None] = mapped_column(String(8))
    content_translated: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(String(8))
    source_type: Mapped[str] = mapped_column(String(32), default="rss")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    entities: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    categories: Mapped[list[str]] = mapped_column(JSON, default=list)
    cluster_id: Mapped[str | None] = mapped_column(String(64))
    raw_snapshot_key: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="raw", index=True)
    ext_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
