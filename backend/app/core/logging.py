"""structlog 结构化日志配置（§6）。

- 开发默认彩色 Console 输出；生产 ``HARBOR_LOG_JSON=true`` 切 JSON（便于采集/检索）
- 通过 ``structlog.contextvars`` 可在请求/任务中绑定上下文（如 request_id、source_id）

对照 CMS：CMS 几乎没有日志层（仅 ai_service 一个 logger）；这里从应用启动就统一走 structlog。
"""

import logging
import sys

import structlog

from app.core.config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """按配置初始化 structlog。应用启动时调用一次。"""
    processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if settings.log_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
    )
