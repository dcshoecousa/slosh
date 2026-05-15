import logging
import sys

from asgi_correlation_id import correlation_id
from loguru import logger
from app.core.settings import BaseAppSettings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logging(settings: BaseAppSettings) -> None:
    logger.remove()
    logger.configure(
        patcher=lambda record: record["extra"].update(
            correlation_id=correlation_id.get() or "-"
        )
    )

    sink_options = {
        "level": settings.log_level.upper(),
        "backtrace": False,
        "diagnose": False,
        "enqueue": True,
        "serialize": settings.log_json,
    }
    if settings.log_json:
        sink_options["format"] = "{message}"
    else:
        sink_options["format"] = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<magenta>{extra[correlation_id]}</magenta> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    logger.add(
        sys.stdout,
        **sink_options,
    )

    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=0, force=True)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [intercept_handler]
        std_logger.propagate = False


def get_logger(name: str):
    return logger.bind(logger_name=name)
