"""任务域数据访问层：crawl_tasks 读写（状态机字段更新）。"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.tasks.models import CrawlTask


class CrawlTaskRepository:
    async def create(self, db: AsyncSession, task: CrawlTask) -> CrawlTask:
        db.add(task)
        await db.flush()
        await db.refresh(task)  # 取回 server_default（created_at 等），否则响应序列化触发 MissingGreenlet
        return task

    async def get(self, db: AsyncSession, task_id: str) -> CrawlTask | None:
        return await db.get(CrawlTask, task_id)

    async def list(
        self,
        db: AsyncSession,
        *,
        source_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[CrawlTask], int]:
        stmt = select(CrawlTask)
        if source_id:
            stmt = stmt.where(CrawlTask.source_id == source_id)
        if status:
            stmt = stmt.where(CrawlTask.status == status)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        rows = (
            await db.execute(
                stmt.order_by(CrawlTask.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars()
        return list(rows), total

    # ---- 状态机（worker 回写，DB 为权威） ----

    async def mark_running(self, db: AsyncSession, task: CrawlTask) -> None:
        task.status = "running"
        task.started_at = datetime.now(UTC)
        await db.flush()

    async def mark_finished(
        self,
        db: AsyncSession,
        task: CrawlTask,
        *,
        status: str,
        result_count: int = 0,
        error: str | None = None,
    ) -> None:
        task.status = status
        task.result_count = result_count
        task.error = error
        task.finished_at = datetime.now(UTC)
        await db.flush()
