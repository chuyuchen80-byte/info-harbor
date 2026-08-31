"""Redis 异步缓存封装（对齐 core/db.py 风格，§6）。

- ``RedisCache``：进程内单例（``get_cache()`` 懒加载），连接串取自 settings（HARBOR_REDIS_URL）
- 验证码用 **Lua 脚本原子「校验即消费」**（GET+DEL 原子化），天然一次性，兼容 Redis 3.0+ 与 GETDEL
- 登录防爆破计数：``incr`` + ``expire nx``（首失败时设置窗口 TTL）
"""

from __future__ import annotations

from functools import lru_cache

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

# 一次性消费脚本：值匹配则删除并返回 1，否则返回 0（不删除 → 同一验证码不可复用）
_CONSUME_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    redis.call('del', KEYS[1])
    return 1
else
    return 0
end
"""


class RedisCache:
    """Redis 薄封装：只暴露本项目用到的操作，连接统一从这里出。"""

    def __init__(self, client: Redis) -> None:
        self._client = client
        self._consume = client.register_script(_CONSUME_SCRIPT)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        await self._client.setex(key, ttl_seconds, value)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def incr(self, key: str) -> int:
        return await self._client.incr(key)

    async def expire(self, key: str, ttl_seconds: int, nx: bool = True) -> bool:
        """设置过期时间；nx=True 时仅在无 TTL 时才设置（避免刷新失败计数窗口）。"""
        return bool(await self._client.expire(key, ttl_seconds, nx=nx))

    async def consume(self, key: str, expected: str) -> bool:
        """原子「校验即消费」：值与 expected 相等则删除并返回 True，否则 False。"""
        return bool(await self._consume(keys=[key], args=[expected]))

    async def aclose(self) -> None:
        await self._client.aclose()


@lru_cache
def get_cache() -> RedisCache:
    """进程内单例。Redis 连接为懒连接，首次调用才建立。"""
    client = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
        encoding="utf-8",
    )
    return RedisCache(client)