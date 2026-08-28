"""异步数据库地基（§6）。

- ``Base``：所有 ORM 模型的声明式基类（Alembic 迁移的 target_metadata）
- ``engine``：异步连接池，进程内单例（模块级创建一次）
- ``AsyncSessionLocal``：异步会话工厂
- ``get_db``：FastAPI 依赖，每个请求一个会话，请求结束自动关闭

对照 CMS：这里是 async SQLAlchemy 版；API 侧每个请求一个 Session 的依赖用法与 CMS 一致，
但 Session 变为异步，commit/query 都要 ``await``。
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """所有 ORM 模型的声明式基类。"""


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,  # 取连接前先探测，避免拿到死连接
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：yield 一个会话，请求结束自动关闭。"""
    async with AsyncSessionLocal() as session:
        yield session


async def dispose_engine() -> None:
    """应用关闭时释放连接池（配合 FastAPI lifespan）。"""
    await engine.dispose()
