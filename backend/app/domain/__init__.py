"""领域模块（每域一个包，同构分层：api / service / repository）。

分层依赖单向：api → service → repository → core/models。
"""

from app.domain import articles, screening, sources, stats, tasks, users

__all__ = ["articles", "screening", "sources", "stats", "tasks", "users"]
