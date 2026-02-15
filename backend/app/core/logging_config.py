"""Structured logging configuration for request/response timing and tracing."""
import logging
import sys
import json
import time
import uuid
from contextvars import ContextVar
from typing import Any

# Correlation ID for request tracing
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if correlation_id_ctx.get():
            log_data["correlation_id"] = correlation_id_ctx.get()
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, default=str)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure application logging with JSON format."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    # Reduce noise from uvicorn/sqlalchemy
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_correlation_id() -> str:
    """Get or create correlation ID for current request."""
    cid = correlation_id_ctx.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id_ctx.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for current request."""
    correlation_id_ctx.set(cid)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with correlation context."""
    return logging.getLogger(name)
