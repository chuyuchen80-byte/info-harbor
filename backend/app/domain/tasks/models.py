"""任务域持久化模型（映射 crawl_tasks 表）。

抓取任务生命周期：queued → running → succeeded | failed。任务状态以 DB 为权威，
ARQ 只负责执行，worker 执行过程中把状态回写 DB（这是异步任务可观测性的核心）。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("sources.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    task_type: Mapped[str] = mapped_column(String(32), default="manual")
    arq_job_id: Mapped[str | None] = mapped_column(String(64))
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
