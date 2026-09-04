"""数据源域业务层：列表 / 详情 / 更新 / YAML seed 幂等 upsert / 触发抓取（§10）。

- service 只依赖契约（core/models）、repository、core/queue，不碰 Request/Response
- seed 规则（D2/D9）：YAML 为配置事实的引导；已存在的源只更新配置字段，
  不覆盖 enabled（避免每次启动把管理员手动关停的源重新打开）
"""

from __future__ import annotations

import uuid
from pathlib import Path

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.models import Source as SourceContract
from app.core.models import SourceUpdate
from app.core.queue import get_arq_pool
from app.domain.sources.models import Source as SourceORM
from app.domain.sources.repository.sources import SourceRepository
from app.domain.tasks.models import CrawlTask
from app.domain.tasks.repository.tasks import CrawlTaskRepository


class SourceNotFoundError(Exception):
    """数据源不存在（api 层映射 404）。"""

    http_status = 404


class SourceService:
    def __init__(self) -> None:
        self.repo = SourceRepository()
        self.task_repo = CrawlTaskRepository()

    # ---- 查询 / 更新 ----

    async def list_sources(self, db: AsyncSession) -> list[SourceContract]:
        rows = await self.repo.list_all(db)
        return [SourceContract.model_validate(row) for row in rows]

    async def overview(self, db: AsyncSession) -> list[dict]:
        """公开的来源产出概况（来源页 / 国家页公开数据，无需登录）。"""
        return await self.repo.overview(db)

    async def get_source(self, db: AsyncSession, source_id: str) -> SourceContract:
        row = await self.repo.get(db, source_id)
        if row is None:
            raise SourceNotFoundError(f"数据源不存在: {source_id}")
        return SourceContract.model_validate(row)

    async def update_source(
        self, db: AsyncSession, source_id: str, payload: SourceUpdate
    ) -> SourceContract:
        row = await self.repo.get(db, source_id)
        if row is None:
            raise SourceNotFoundError(f"数据源不存在: {source_id}")
        row = await self.repo.update(
            db, row, enabled=payload.enabled, weight=payload.weight
        )
        await db.commit()
        return SourceContract.model_validate(row)

    # ---- seed（lifespan 启动引导，D2） ----

    async def seed_from_config(self, db: AsyncSession) -> int:
        """读 config/sources/*.yaml，幂等 upsert 进 DB。返回处理的源数。"""
        seed_dir = Path(get_settings().source_config_dir)
        if not seed_dir.is_dir():
            return 0
        count = 0
        for path in sorted(seed_dir.glob("*.yaml")):
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for item in payload.get("sources") or []:
                if "id" not in item:
                    continue
                existing = await self.repo.get(db, item["id"])
                if existing is None:
                    db.add(
                        SourceORM(
                            id=item["id"],
                            name=item.get("name", item["id"]),
                            country=item.get("country"),
                            type=item.get("type", "media"),
                            adapter_key=item.get("adapter_key", item["id"]),
                            config=item.get("config") or {},
                            weight=item.get("weight", 1.0),
                            enabled=bool(item.get("enabled", True)),
                        )
                    )
                else:
                    # 幂等：只同步配置事实，不动 enabled（见模块 docstring）
                    existing.name = item.get("name", existing.name)
                    existing.country = item.get("country", existing.country)
                    existing.adapter_key = item.get("adapter_key", existing.adapter_key)
                    existing.weight = item.get("weight", existing.weight)
                    if item.get("config"):
                        existing.config = item["config"]
                count += 1
        await db.flush()
        return count

    # ---- 触发抓取 ----

    async def trigger_crawl(
        self, db: AsyncSession, source_id: str, *, task_type: str = "manual"
    ) -> CrawlTask:
        """建 CrawlTask(queued) 并入队 ARQ；执行在 worker 进程（§6.2）。"""
        source = await self.repo.get(db, source_id)
        if source is None:
            raise SourceNotFoundError(f"数据源不存在: {source_id}")

        task = CrawlTask(
            id=uuid.uuid4().hex,
            source_id=source.id,
            status="queued",
            task_type=task_type,
        )
        await self.task_repo.create(db, task)

        pool = await get_arq_pool()
        job = await pool.enqueue_job("crawl_source", source.id, task.id)
        task.arq_job_id = job.job_id if job else None
        await db.commit()
        return task
