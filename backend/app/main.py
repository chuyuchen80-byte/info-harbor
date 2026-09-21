"""info-harbor 后端入口：路由挂载 / 中间件 / 事件装配。

启动（开发）：
    cd backend
    uvicorn app.main:app --reload
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.db import AsyncSessionLocal, dispose_engine
from app.core.events import EventBus, register_domain_events
from app.domain.articles.api.router import router as articles_router
from app.domain.sources.api.router import router as sources_router
from app.domain.sources.service.sources import SourceService
from app.domain.tasks.api.router import router as tasks_router
from app.domain.users.api.router import router as users_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """启动引导：YAML seed 幂等 upsert sources（D2）；关闭时释放连接池。"""
    async with AsyncSessionLocal() as db:
        seeded = await SourceService().seed_from_config(db)
        await db.commit()
    if seeded:
        print(f"[lifespan] seed 完成：config/sources 共处理 {seeded} 个源")
    yield
    await dispose_engine()


app = FastAPI(
    title="info-harbor API",
    version="0.1.0",
    description="聚合全球多源 AI 动态，经 LLM 筛选评估后按国家/地区维度展示。",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 事件总线：in-process 起步，多 worker 后切换 Redis Streams（§4-②）
bus = EventBus()
register_domain_events(bus)


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}


# 按领域挂载（§10）：新增领域 = 新增 router + 一行 include_router
app.include_router(articles_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(sources_router, prefix=settings.api_prefix)
app.include_router(tasks_router, prefix=settings.api_prefix)
