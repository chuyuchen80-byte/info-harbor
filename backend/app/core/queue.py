"""ARQ 入队客户端（outbound adapter，API 进程侧）。

- 进程内单例懒加载 arq pool，连接 ``task_queue_url``（与 worker 同一个 Redis 库）
- API 经 service 触发抓取时用它 enqueue；执行在 worker 进程（§6.2）
- 对齐 core/cache.py 的单例风格
"""

from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import get_settings

_pool: ArqRedis | None = None


async def get_arq_pool() -> ArqRedis:
    """进程内单例。首次调用才建连（懒加载）。"""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = await create_pool(RedisSettings.from_dsn(settings.task_queue_url))
    return _pool
