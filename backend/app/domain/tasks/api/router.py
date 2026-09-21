"""任务域 API（inbound adapter）：任务列表 / 详情（admin）。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.models import UserOut
from app.domain.tasks.service.tasks import TaskNotFoundError, TaskService
from app.domain.users.api.deps import require_roles

router = APIRouter(prefix="/tasks", tags=["tasks"])

_admin = Depends(require_roles("admin"))


@router.get("", summary="抓取任务列表（分页，可按源/状态筛选）")
async def list_tasks(
    source_id: str | None = None,
    task_status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: TaskService = Depends(TaskService),  # noqa: B008
    _: UserOut = _admin,  # noqa: B008
) -> dict[str, Any]:
    """最近的抓取任务，管理页任务监控用（created_at 倒序）。"""
    return await service.list_tasks(
        db, source_id=source_id, status=task_status, page=page, page_size=page_size
    )


@router.get("/{task_id}", summary="任务详情")
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: TaskService = Depends(TaskService),  # noqa: B008
    _: UserOut = _admin,  # noqa: B008
) -> dict[str, Any]:
    try:
        task = await service.get_task(db, task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    return task.model_dump()
