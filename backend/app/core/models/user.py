"""统一用户/认证契约（§7）：User / Register / Login / Token / Captcha 的 Pydantic v2 定义。

规则：
- 所有字段蛇形命名（与现有契约、前端 http.ts 拦截行为保持一致，前端按需映射）
- 密码任何情况下不进响应模型；``UserInDB`` 仅仓库层使用，永不序列化输出
- ``role`` / ``status`` 为 RBAC 预留：本轮只落默认值，鉴权逻辑后续接入
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserOut(UserBase):
    id: str
    role: str = "user"
    status: str = "active"
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserOut):
    """仓库内部模型：含密码哈希。禁止作为响应体/离开服务层。"""

    password_hash: str


class UserRegister(BaseModel):
    """注册请求体：附带验证码。"""

    username: str = Field(min_length=2, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    captcha_id: str
    captcha_code: str


class UserLogin(BaseModel):
    """登录请求体：account 为用户名或邮箱（含 @ 视为邮箱）。"""

    account: str
    password: str
    captcha_id: str
    captcha_code: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CaptchaResponse(BaseModel):
    """验证码接口响应：id 用于回传，image 为 data:image/png;base64。"""

    captcha_id: str
    image_base64: str