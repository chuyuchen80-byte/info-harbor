"""统一数据契约（单一权威，§7）。所有层通过这里交互，禁止各域各建一份。"""

from app.core.models.article import Article, Entity, Score, Source, SourceUpdate
from app.core.models.task import TaskOut
from app.core.models.user import (
    CaptchaResponse,
    Token,
    UserBase,
    UserCreate,
    UserInDB,
    UserLogin,
    UserOut,
    UserRegister,
)

__all__ = [
    "Article",
    "CaptchaResponse",
    "Entity",
    "Score",
    "Source",
    "SourceUpdate",
    "TaskOut",
    "Token",
    "UserBase",
    "UserCreate",
    "UserInDB",
    "UserLogin",
    "UserOut",
    "UserRegister",
]
