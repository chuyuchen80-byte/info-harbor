"""认证 API 路由（inbound adapter，§10）：只做参数接收 → 调 service → 返回响应。

错误映射：service 抛 ``AuthError``（带 http_status/detail）→ 这里转 ``HTTPException``。
验证码端点：Pillow 渲染用 ``asyncio.to_thread`` 扔到线程池，Redis 写入仍走异步，不阻塞事件循环。
"""

from __future__ import annotations

import asyncio
import base64
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache
from app.core.captcha import generate_captcha
from app.core.config import get_settings
from app.core.db import get_db
from app.core.models import CaptchaResponse, Token, UserLogin, UserOut, UserRegister
from app.domain.users.api.deps import get_current_user
from app.domain.users.service.auth import AuthError, AuthService, get_auth_service

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/captcha", response_model=CaptchaResponse, summary="获取图形验证码")
async def get_captcha() -> CaptchaResponse:
    """生成图形验证码：返回 captcha_id（回传校验）与 base64 PNG（前端渲染，点击可刷新）。

    验证码存 Redis（TTL 内有效、一次性消费），无需登录即可调用。
    """
    code, png = await asyncio.to_thread(generate_captcha, settings.captcha_length)
    captcha_id = uuid.uuid4().hex
    # 存小写，校验时大小写不敏感
    await get_cache().setex(
        f"captcha:{captcha_id}", settings.captcha_ttl_seconds, code.lower()
    )
    return CaptchaResponse(
        captcha_id=captcha_id,
        image_base64=base64.b64encode(png).decode("ascii"),
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="注册账号",
)
async def register(
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> UserOut:
    """注册：需先获取验证码。注册成功不自动登录，前端切到登录模式。"""
    try:
        return await service.register(db, payload)
    except AuthError as exc:
        raise HTTPException(status_code=exc.http_status, detail=exc.detail) from None


@router.post("/login", response_model=Token, summary="登录获取 token")
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> Token:
    """登录：account 为用户名或邮箱，需验证码。失败 5 次/5 分钟锁定（429）。"""
    try:
        return await service.login(db, payload)
    except AuthError as exc:
        raise HTTPException(status_code=exc.http_status, detail=exc.detail) from None


@router.get("/me", response_model=UserOut, summary="当前登录用户信息")
async def me(
    user: UserOut = Depends(get_current_user),  # noqa: B008
) -> UserOut:
    """校验 Bearer token 并返回当前用户（含 role/status，供前端权限判断）。"""
    return user