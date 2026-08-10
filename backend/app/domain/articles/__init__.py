"""文章域：核心内容域，MVP 最小闭环的落点。

分层：api（adapters/inbound）→ service（application）→ repository（adapters/outbound）。
"""

from __future__ import annotations

from app.core.events import EventBus


def register(bus: EventBus) -> None:
    """注册本域的事件 handler（域实现后填充）。"""
