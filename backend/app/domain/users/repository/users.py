"""用户域数据访问层（outbound adapter）：持有 db 会话做 CRUD，不写业务逻辑。

方法统一接收 ``db: AsyncSession`` 参数（不持有 session，符合六边形依赖单向）；
返回 ORM ``User`` 对象，由 service 层转换为统一契约（core/models/user.py）。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.models import User


class UserRepository:
    async def get_by_id(self, db: AsyncSession, user_id: str) -> User | None:
        return await db.get(User, user_id)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        return await db.scalar(select(User).where(User.username == username))

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        return await db.scalar(select(User).where(User.email == email))

    async def get_by_account(self, db: AsyncSession, account: str) -> User | None:
        """按用户名或邮箱查用户（含 @ 优先按邮箱精确匹配，再按用户名匹配）。"""
        stmt = select(User).where(
            or_(User.username == account, User.email == account)
        )
        return await db.scalar(stmt)

    async def exists(self, db: AsyncSession, username: str, email: str) -> bool:
        stmt = select(func.count()).select_from(User).where(
            or_(User.username == username, User.email == email)
        )
        count = await db.scalar(stmt)
        return bool(count)

    async def create(self, db: AsyncSession, user: User) -> User:
        """落库并 flush（拿到 id/时间戳），事务提交由 service 负责。"""
        db.add(user)
        await db.flush()
        return user

    async def update_login_time(self, db: AsyncSession, user: User, now: datetime) -> None:
        user.last_login_at = now
        await db.flush()