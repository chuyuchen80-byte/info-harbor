"""数据源域数据访问层（outbound adapter）：持有 session，只做读写，无业务逻辑。"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.articles.models import Article as ArticleORM
from app.domain.sources.models import Source


class SourceRepository:
    async def overview(self, db: AsyncSession) -> list[dict]:
        """公开聚合：每个源的产出概况（文章数 / 最近发布时间）。

        跨域只读：仅聚合 articles 的 count/max，不加载文章行（来源页公开数据）。
        """
        stmt = (
            select(
                Source.id,
                Source.name,
                Source.country,
                Source.type,
                Source.adapter_key,
                Source.enabled,
                func.count(ArticleORM.id).label("article_count"),
                func.max(ArticleORM.published_at).label("last_published_at"),
            )
            .outerjoin(ArticleORM, ArticleORM.source_id == Source.id)
            .group_by(Source.id)
            .order_by(func.count(ArticleORM.id).desc())
        )
        rows = (await db.execute(stmt)).all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "country": r.country,
                "type": r.type,
                "adapter_key": r.adapter_key,
                "enabled": r.enabled,
                "article_count": r.article_count,
                "last_published_at": r.last_published_at,
            }
            for r in rows
        ]

    async def list_all(
        self, db: AsyncSession, *, enabled_only: bool = False
    ) -> list[Source]:
        stmt = select(Source).order_by(Source.created_at)
        if enabled_only:
            stmt = stmt.where(Source.enabled.is_(True))
        return list((await db.execute(stmt)).scalars())

    async def get(self, db: AsyncSession, source_id: str) -> Source | None:
        return await db.get(Source, source_id)

    async def update(
        self,
        db: AsyncSession,
        source: Source,
        *,
        enabled: bool | None = None,
        weight: float | None = None,
    ) -> Source:
        """部分更新：只改给出的字段（PATCH 语义）。"""
        if enabled is not None:
            source.enabled = enabled
        if weight is not None:
            source.weight = weight
        await db.flush()
        return source
