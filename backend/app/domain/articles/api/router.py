"""文章域 API（adapters/inbound）。MVP：占位路由，数据源后续接入。"""

from fastapi import APIRouter

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
async def list_articles(
    page: int = 1,
    page_size: int = 20,
    country: str | None = None,
    source_id: str | None = None,
    min_score: float | None = None,
    sort: str = "published_at",
) -> dict:
    """文章列表：分页 / 过滤 / 排序（§10）。骨架阶段返回空集。"""
    return {"items": [], "page": page, "page_size": page_size, "total": 0}


@router.get("/{article_id}")
async def get_article(article_id: str) -> dict:
    """文章详情（含评分明细 / 实体 / 相关，§10）。"""
    return {"id": article_id, "detail": "TODO"}
