"""抓取任务契约（§7 扩展）：crawl_tasks 表的响应形状。

任务状态以 DB 为权威（queued → running → succeeded | failed），ARQ 只负责执行。
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskOut(BaseModel):
    """任务响应契约：管理页任务监控 / 触发抓取的返回形状。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    status: str  # queued / running / succeeded / failed
    task_type: str  # manual / scheduled
    arq_job_id: str | None = None
    result_count: int = 0
    error: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
