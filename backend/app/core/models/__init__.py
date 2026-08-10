"""统一数据契约（单一权威，§7）。所有层通过这里交互，禁止各域各建一份。"""

from app.core.models.article import Article, Entity, Score, Source

__all__ = ["Article", "Entity", "Score", "Source"]
