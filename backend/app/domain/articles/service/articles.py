"""文章域业务层：文章列表 / 详情（M1 真实化，替换骨架占位）。"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Article as ArticleContract
from app.domain.articles.repository.articles import ArticleRepository

_SORT_WHITELIST = {"published_at", "created_at"}


class ArticleNotFoundError(Exception):
    """文章不存在（api 层映射 404）。"""

    http_status = 404


class ArticleService:
    def __init__(self) -> None:
        self.repo = ArticleRepository()

    async def list_articles(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        country: str | None = None,
        source_id: str | None = None,
        sort: str = "published_at",
    ) -> dict:
        items, total = await self.repo.list_articles(
            db,
            page=page,
            page_size=page_size,
            country=country,
            source_id=source_id,
            sort=sort if sort in _SORT_WHITELIST else "published_at",
        )
        return {
            "items": [ArticleContract.model_validate(row) for row in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_article(self, db: AsyncSession, article_id: str) -> ArticleContract:
        row = await self.repo.get(db, article_id)
        if row is None:
            raise ArticleNotFoundError(f"文章不存在: {article_id}")
        return ArticleContract.model_validate(row)
