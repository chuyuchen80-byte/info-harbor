"""用户域业务层：注册 / 登录 / 验证码 / 防爆破 / 当前用户（§10）。

规则（六边形）：
- service 只依赖：契约（core/models）、repository、core/cache、core/security，不接收 Request / 返回 HTTPResponse
- 错误用 ``AuthError`` 异常体系上抛，由 api 层统一映射为 HTTPException
- 验证码与防爆破计数存 Redis（``core/cache.RedisCache``）
"""

from __future__ import annotations

import base64
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import RedisCache, get_cache
from app.core.captcha import generate_captcha
from app.core.config import Settings, get_settings
from app.core.models import CaptchaResponse, Token, UserLogin, UserOut, UserRegister
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.users.models import User
from app.domain.users.repository.users import UserRepository

settings = get_settings()


class AuthError(Exception):
    """认证业务错误基类：携带 HTTP 状态码与可读信息（api 层映射）。"""

    http_status = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class CaptchaError(AuthError):
    """验证码缺失/错误/已过期/已使用。"""

    http_status = 400


class InvalidCredentialsError(AuthError):
    """账号不存在或密码错误。"""

    http_status = 401


class UserAlreadyExistsError(AuthError):
    """用户名或邮箱已存在。"""

    http_status = 409


class TooManyAttemptsError(AuthError):
    """登录失败次数超限（防爆破）。"""

    http_status = 429


class AuthService:
    def __init__(
        self,
        cache: RedisCache | None = None,
        repo: UserRepository | None = None,
        cfg: Settings | None = None,
    ) -> None:
        self.cache = cache or get_cache()
        self.repo = repo or UserRepository()
        self.cfg = cfg or settings

    # ---- 验证码 ----

    async def create_captcha(self) -> CaptchaResponse:
        """生成验证码：写 Redis（TTL 内有效、一次性），返回 base64 PNG 给前端渲染。"""
        code, png = generate_captcha(self.cfg.captcha_length)
        captcha_id = uuid.uuid4().hex
        await self.cache.setex(
            f"captcha:{captcha_id}", self.cfg.captcha_ttl_seconds, code.lower()
        )
        encoded = base64.b64encode(png).decode("ascii")
        return CaptchaResponse(captcha_id=captcha_id, image_base64=encoded)

    async def _verify_captcha(self, captcha_id: str, captcha_code: str) -> None:
        """原子「校验即消费」：错误/过期/复用都抛 CaptchaError，且验证码被删除后不可再用。"""
        if not captcha_id or not captcha_code:
            raise CaptchaError("验证码缺失")
        ok = await self.cache.consume(
            f"captcha:{captcha_id}", captcha_code.strip().lower()
        )
        if not ok:
            raise CaptchaError("验证码错误或已过期")

    # ---- 注册 / 登录 ----

    async def register(self, db: AsyncSession, payload: UserRegister) -> UserOut:
        await self._verify_captcha(payload.captcha_id, payload.captcha_code)

        if await self.repo.exists(db, payload.username, payload.email):
            raise UserAlreadyExistsError("用户名或邮箱已被注册")

        user = User(
            id=uuid.uuid4().hex,
            username=payload.username,
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            role="user",  # RBAC 预留：默认普通用户
            status="active",
        )
        created = await self.repo.create(db, user)
        await db.commit()
        return UserOut.model_validate(created)

    async def login(self, db: AsyncSession, payload: UserLogin) -> Token:
        await self._verify_captcha(payload.captcha_id, payload.captcha_code)

        account = payload.account.strip()
        fail_key = f"login_fail:{account.lower()}"
        if await self._too_many_failures(fail_key):
            raise TooManyAttemptsError("登录失败次数过多，请稍后再试")

        user = await self.repo.get_by_account(db, account)
        if user is None or not verify_password(payload.password, user.password_hash):
            await self._record_failure(fail_key)
            raise InvalidCredentialsError("账号或密码错误")

        if user.status != "active":
            raise InvalidCredentialsError("账号已被停用")

        # 登录成功：清失败计数 + 记录最近登录时间
        await self.cache.delete(fail_key)
        await self.repo.update_login_time(db, user, datetime.now(UTC))
        await db.commit()

        token = create_access_token(subject=user.id, role=user.role)
        return Token(access_token=token)

    async def get_user(self, db: AsyncSession, user_id: str) -> UserOut:
        """按 id 拉最新用户（role/status 每次从库取，保证权限变更即时生效）。"""
        user = await self.repo.get_by_id(db, user_id)
        if user is None:
            raise InvalidCredentialsError("用户不存在或已注销")
        return UserOut.model_validate(user)

    # ---- 防爆破（内部） ----

    async def _too_many_failures(self, key: str) -> bool:
        val = await self.cache.get(key)
        return val is not None and int(val) >= self.cfg.login_max_failures

    async def _record_failure(self, key: str) -> None:
        await self.cache.incr(key)
        # 首次失败时设置窗口 TTL（nx=True 不刷新已存在的窗口）
        await self.cache.expire(key, self.cfg.login_fail_window_seconds, nx=True)


# 供 api 层注入的构建函数（轻量容器）
def get_auth_service() -> AuthService:
    return AuthService()