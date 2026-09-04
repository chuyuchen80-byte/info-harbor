"""ARQ worker 入口（§4-① / §6.2）——M1 爬虫执行端。

- ``crawl_source``：单源抓取任务。任务状态以 DB 为权威（crawl_tasks），ARQ 只负责执行
- 定时（D11）：arq 原生 cron 每 ``HARBOR_CRAWL_INTERVAL_HOURS`` 小时把全量 enabled 源入队
  （原计划 APScheduler 属过度设计：同进程再养一个调度器不如用 arq 自带 cron，且 unique=True
  天然防重复入队；tasks extras 里的 apscheduler 保留给未来更复杂调度）

运行：cd backend && .venv/bin/arq app.worker.WorkerSettings
"""

from __future__ import annotations

import uuid
from typing import Any

from arq import cron
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.db import AsyncSessionLocal
from app.core.events import ArticleRawIngested, EventBus
from app.core.models import Source as SourceContract
from app.domain.articles.repository.articles import ArticleRepository
from app.domain.sources.models import Source as SourceORM
from app.domain.sources.repository.sources import SourceRepository
from app.domain.tasks.models import CrawlTask
from app.domain.tasks.repository.tasks import CrawlTaskRepository
from app.plugins.sources import registry

settings = get_settings()
bus = EventBus()

_ERROR_TRUNC = 2000  # task.error 为 TEXT，错误摘要超长截断


async def crawl_source(ctx: dict[str, Any], source_id: str, task_id: str) -> None:
    """单源抓取：列表 → 逐条去重 → 详情正文 → normalize → 落库；状态回写 crawl_tasks。

    - 单条失败只记入 task.error，不中断整源（每条独立提交）
    - 任务不存在/源不存在：直接返回（ARQ 侧重试无意义）
    """
    async with AsyncSessionLocal() as db:
        task_repo = CrawlTaskRepository()
        task = await task_repo.get(db, task_id)
        source_orm = await db.get(SourceORM, source_id)
        if task is None or source_orm is None:
            return

        await task_repo.mark_running(db, task)
        await db.commit()

        plugin = registry.get(source_orm.adapter_key)
        if plugin is None:
            await task_repo.mark_finished(
                db, task, status="failed", error=f"未注册的适配器: {source_orm.adapter_key}"
            )
            await db.commit()
            return

        source = SourceContract.model_validate(source_orm)
        article_repo = ArticleRepository()

        try:
            items = await plugin.list_items(source)
        except Exception as exc:  # 列表失败 = 整源失败
            await task_repo.mark_finished(db, task, status="failed", error=f"列表抓取失败: {exc}")
            await db.commit()
            return

        new_count = 0
        errors: list[str] = []
        for item in items:
            url = item.get("url") or ""
            if not url or await article_repo.exists_url(db, url):
                continue
            try:
                detail = await plugin.fetch_detail(item)
                article = plugin.normalize(item, detail, source=source)
                await article_repo.create(db, article)
                await db.commit()  # 每条一提交：单条失败不影响已入库文章
                new_count += 1
                await bus.publish(
                    ArticleRawIngested(
                        aggregate_id=article.id, article_id=article.id, source_id=source.id
                    )
                )
            except Exception as exc:
                await db.rollback()
                errors.append(f"{url}: {exc}")

        await task_repo.mark_finished(
            db,
            task,
            status="succeeded",
            result_count=new_count,
            error=("；".join(errors)[:_ERROR_TRUNC] or None),
        )
        await db.commit()


async def enqueue_enabled_sources(ctx: dict[str, Any]) -> None:
    """定时任务体：全量 enabled 源各建一个 scheduled CrawlTask 并入队。"""
    async with AsyncSessionLocal() as db:
        sources = await SourceRepository().list_all(db, enabled_only=True)
        pool = ctx["redis"]  # worker 自带的 arq pool
        for source in sources:
            task = CrawlTask(
                id=uuid.uuid4().hex,
                source_id=source.id,
                status="queued",
                task_type="scheduled",
            )
            await CrawlTaskRepository().create(db, task)
            await pool.enqueue_job("crawl_source", source.id, task.id)
        await db.commit()
        if sources:
            print(f"[cron] 已入队 {len(sources)} 个源的定时抓取")


def _crawl_hours() -> set[int]:
    """由 HARBOR_CRAWL_INTERVAL_HOURS 推出 cron 触发小时集合（12 → {0,12}，24 → {0}）。"""
    interval = min(max(1, settings.crawl_interval_hours), 24)
    return {hour % 24 for hour in range(0, 24, interval)}


class WorkerSettings:
    """arq worker 配置（T8 修复：显式接 task_queue_url，不再落默认 db0）。"""

    functions = [crawl_source]
    cron_jobs = [
        cron(
            enqueue_enabled_sources,
            minute=0,
            hour=_crawl_hours(),
            unique=True,  # 防重复入队（上一次还没跑完不会叠加）
            run_at_startup=False,
        )
    ]
    redis_settings = RedisSettings.from_dsn(settings.task_queue_url)
