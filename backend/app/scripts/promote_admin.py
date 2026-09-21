"""运维小工具：把指定用户创建/提为 admin（RBAC 接线 D7），可选打印调试 token。

用法（backend 目录下）：
    .venv/bin/python -m app.scripts.promote_admin <username> [--password <pw>] [--no-token]

- 用户不存在且给了 --password → 直接创建（role=admin，email 占位 <username>@harbor.dev，
  域名需能过 EmailStr 校验——保留域/不可投递域会被拒）
- 用户存在 → role 提为 admin
- 默认打印一个新签发的 JWT（24h，与登录同源），供本地验收管理接口
"""

from __future__ import annotations

import argparse
import asyncio
import uuid

from sqlalchemy import select

from app.core.db import AsyncSessionLocal, dispose_engine
from app.core.security import create_access_token, hash_password
from app.domain.users.models import User


async def run(username: str, password: str | None, print_token: bool) -> None:
    async with AsyncSessionLocal() as db:
        user = (
            (await db.execute(select(User).where(User.username == username)))
            .scalars()
            .first()
        )
        created = False
        if user is None:
            if not password:
                raise SystemExit(f"用户 {username!r} 不存在；请加 --password 直接创建")
            user = User(
                id=uuid.uuid4().hex,
                username=username,
                email=f"{username}@harbor.dev",  # 占位域名：需通过 EmailStr 校验（.local 等保留域会被拒）
                password_hash=hash_password(password),
                role="admin",
                status="active",
            )
            db.add(user)
            created = True
            action = "创建 admin 用户"
        else:
            user.role = "admin"
            action = "提升为 admin"
        await db.commit()
        print(f"[ok] {action}: {username}")
        if print_token:
            print("[token]", create_access_token(subject=user.id, role="admin"))
    await dispose_engine()  # 脚本退出前释放连接池，避免 loop 关闭后连接回收报错


def main() -> None:
    parser = argparse.ArgumentParser(description="创建/提升 admin 用户（可打印调试 token）")
    parser.add_argument("username", help="目标用户名")
    parser.add_argument("--password", default=None, help="用户不存在时用该密码创建")
    parser.add_argument("--no-token", action="store_true", help="不打印 token")
    args = parser.parse_args()
    asyncio.run(run(args.username, args.password, not args.no_token))


if __name__ == "__main__":
    main()
