"""任务域业务层：任务列表 / 详情（M1 只读；retry/cancel 留下轮）。"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import TaskOut
from app.domain.tasks.repository.tasks import CrawlTaskRepository


class TaskNotFoundError(Exception):
    """任务不存在（api 层映射 404）。"""

    http_status = 404


class TaskService:
    def __init__(self) -> None:
        self.repo = CrawlTaskRepository()

    async def list_tasks(
        self,
        db: AsyncSession,
        *,
        source_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        rows, total = await self.repo.list(
            db, source_id=source_id, status=status, page=page, page_size=page_size
        )
        return {
            "items": [TaskOut.model_validate(row) for row in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_task(self, db: AsyncSession, task_id: str) -> TaskOut:
        row = await self.repo.get(db, task_id)
        if row is None:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        return TaskOut.model_validate(row)
