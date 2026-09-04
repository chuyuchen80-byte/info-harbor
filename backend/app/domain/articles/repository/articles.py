"""文章域数据访问层：文章读写。

去重（D4）：``url`` 唯一索引为权威；写入前预查做快路径，
并发撞上唯一约束时由调用方捕获 IntegrityError 跳过（单 worker MVP 下预查已足够）。
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Article as ArticleContract
from app.domain.articles.models import Article as ArticleORM


class ArticleRepository:
    async def exists_url(self, db: AsyncSession, url: str) -> bool:
        stmt = select(ArticleORM.id).where(ArticleORM.url == url).limit(1)
        return (await db.execute(stmt)).scalar() is not None

    async def create(self, db: AsyncSession, article: ArticleContract) -> ArticleORM:
        """契约 → ORM 落库（字段名一一对应；JSON 列直接存 list/dict）。"""
        row = ArticleORM(**article.model_dump())
        db.add(row)
        await db.flush()
        return row

    async def get(self, db: AsyncSession, article_id: str) -> ArticleORM | None:
        return await db.get(ArticleORM, article_id)

    async def list_articles(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        country: str | None = None,
        source_id: str | None = None,
        sort: str = "published_at",
    ) -> tuple[list[ArticleORM], int]:
        stmt = select(ArticleORM)
        if country:
            stmt = stmt.where(ArticleORM.country == country)
        if source_id:
            stmt = stmt.where(ArticleORM.source_id == source_id)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()

        # 排序字段白名单；published_at 为 NULL 的排最后（MySQL DESC 下 NULL 在前的坑）
        sort_column = {
            "published_at": ArticleORM.published_at,
            "created_at": ArticleORM.created_at,
        }.get(sort, ArticleORM.published_at)
        stmt = stmt.order_by(
            sort_column.is_(None), sort_column.desc(), ArticleORM.created_at.desc()
        )
        rows = (
            await db.execute(
                stmt.offset((page - 1) * page_size).limit(page_size)
            )
        ).scalars()
        return list(rows), total
