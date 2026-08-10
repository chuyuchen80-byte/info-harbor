"""ARQ worker 入口（§4-① / §6.2）。

APScheduler 只负责把周期任务入队 ARQ；ARQ 负责异步执行 / 重试 / 背压 / DLQ。
运行：
    cd backend && pip install -e ".[tasks]" && arq app.worker.WorkerSettings
"""

from __future__ import annotations

from app.core.events import ArticleRawIngested, EventBus

bus = EventBus()


async def run_pipeline(ctx: dict, article_id: str, source_id: str) -> None:
    """占位任务：抓取 → 清洗 → 规则初筛（MVP 最小闭环，后续实现）。"""
    # 示例：发布事件驱动下游管道
    await bus.publish(ArticleRawIngested(article_id=article_id, source_id=source_id))


class WorkerSettings:
    functions = [run_pipeline]
