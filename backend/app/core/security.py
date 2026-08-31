"""认证安全基元：密码哈希（pwdlib/bcrypt）+ JWT 签发与校验（PyJWT）。

纯同步、无 IO，任何层可直接调用。密钥/有效期来自 ``core/config``（HARBOR_JWT_*）。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import JWT_ALGORITHM, get_settings

settings = get_settings()

# pwdlib 0.3 在只安装 bcrypt 时 PasswordHash.recommended() 会尝试导入 argon2 并抛错，
# 故直接显式只用 bcrypt hasher（FastAPI 官方 docs 同属一个哈希抽象，见 DECISIONS.md D7）。
_password_hasher = PasswordHash([BcryptHasher()])


def hash_password(plain: str) -> str:
    """密码哈希（bcrypt，自动加盐）。"""
    return _password_hasher.hash(plain)


def verify_password(plain: str, password_hash: str) -> bool:
    """校验明文与哈希是否匹配。"""
    return _password_hasher.verify(plain, password_hash)


def create_access_token(subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
    """签发访问令牌：payload = {sub, role, type, iat, exp}。

    - ``sub`` 为用户 id（字符串）
    - ``role`` 随 token 携带，供未来 RBAC 快速判断（权威仍以 DB 为准，见 get_user）
    """
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """校验并解析令牌，返回 payload。

    抛 ``jwt.ExpiredSignatureError`` / ``jwt.InvalidTokenError``（上层转为 401）。
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])