"""数据源域 API（inbound adapter）：参数接收 → service → 响应；业务错误映射 HTTPException。

管理接口全部 `require_roles("admin")`（RBAC 接线，DECISIONS D7/D12）。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.models import Source, SourceUpdate, TaskOut, UserOut
from app.domain.sources.service.sources import (
    SourceNotFoundError,
    SourceService,
)
from app.domain.users.api.deps import require_roles

router = APIRouter(prefix="/sources", tags=["sources"])

_admin = Depends(require_roles("admin"))


@router.get("/overview", summary="来源产出概况（公开）")
async def source_overview(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: SourceService = Depends(SourceService),  # noqa: B008
) -> list[dict[str, object]]:
    """每源文章数与最近发布时间，来源页公开数据（无需登录）。"""
    return await service.overview(db)


@router.get("", response_model=list[Source], summary="数据源列表")
async def list_sources(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: SourceService = Depends(SourceService),  # noqa: B008
    _: UserOut = _admin,  # noqa: B008
) -> list[Source]:
    """全量数据源（含未启用的），管理页源管理用。"""
    return await service.list_sources(db)


@router.get("/{source_id}", response_model=Source, summary="数据源详情")
async def get_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: SourceService = Depends(SourceService),  # noqa: B008
    _: UserOut = _admin,  # noqa: B008
) -> Source:
    try:
        return await service.get_source(db, source_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None


@router.patch("/{source_id}", response_model=Source, summary="更新数据源（启停/权重）")
async def update_source(
    source_id: str,
    payload: SourceUpdate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: SourceService = Depends(SourceService),  # noqa: B008
    _: UserOut = _admin,  # noqa: B008
) -> Source:
    try:
        return await service.update_source(db, source_id, payload)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None


@router.post("/{source_id}/crawl", response_model=TaskOut, status_code=status.HTTP_202_ACCEPTED,
             summary="触发一次抓取（手动）")
async def trigger_crawl(
    source_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: SourceService = Depends(SourceService),  # noqa: B008
    _: UserOut = _admin,  # noqa: B008
) -> TaskOut:
    """建 CrawlTask(queued) 并入队 ARQ；任务执行与状态流转见 tasks 域。"""
    try:
        return await service.trigger_crawl(db, source_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
