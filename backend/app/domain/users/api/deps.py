"""认证 API 依赖（inbound adapter）：Bearer token → 当前用户。

- ``get_current_user``：任何需要登录的接口注入它即可
- ``require_roles(*roles)``：RBAC 扩展点（本轮预留不接线，见 DECISIONS.md D7）。
  将来把 ``Depends(get_current_user)`` 换成 ``Depends(require_roles("admin"))`` 即可。
"""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.models import UserOut
from app.core.security import decode_access_token
from app.domain.users.service.auth import (
    AuthError,
    AuthService,
    get_auth_service,
)

# auto_error=False：缺 Authorization 头时返回 None，由我们统一给 401 语义
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> UserOut:
    """解析并校验 token，返回 DB 中的最新用户信息（每次实时取，权限变更即时生效）。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或凭证缺失",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期，请重新登录"
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的登录凭证"
        ) from None

    try:
        return await service.get_user(db, payload["sub"])
    except AuthError as exc:
        raise HTTPException(status_code=exc.http_status, detail=exc.detail) from None


def require_roles(*roles: str):
    """RBAC 扩展点：校验当前用户角色在允许列表内。本轮实现后接线到 /admin 等路由。"""

    async def checker(
        user: UserOut = Depends(get_current_user),  # noqa: B008
    ) -> UserOut:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有访问权限（需要角色: " + ", ".join(roles) + "）",
            )
        return user

    return checker