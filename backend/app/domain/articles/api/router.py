"""文章域 API（inbound adapter）：M1 真实化——分页列表 / 详情走 service→repository。

公开接口（不要求登录）；管理类操作在 sources/tasks 域。
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.models import Article
from app.domain.articles.service.articles import ArticleNotFoundError, ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", summary="文章列表（分页/国家/来源/排序）")
async def list_articles(
    page: int = 1,
    page_size: int = 20,
    country: str | None = None,
    source_id: str | None = None,
    sort: str = "published_at",  # published_at | created_at
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: ArticleService = Depends(ArticleService),  # noqa: B008
) -> dict[str, Any]:
    """文章列表；published_at 为空的文章排最后。min_score 筛选待评分管道后开放。"""
    return await service.list_articles(
        db, page=page, page_size=page_size, country=country, source_id=source_id, sort=sort
    )


@router.get("/{article_id}", response_model=Article, summary="文章详情")
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: ArticleService = Depends(ArticleService),  # noqa: B008
) -> Article:
    try:
        return await service.get_article(db, article_id)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
