"""
Centralized logging configuration for FactGuard backend.
Provides structured logging with support for different formats.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Custom formatter that outputs logs as formatted text."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"[{timestamp}] {record.levelname:<8} "
            f"{record.name}:{record.funcName}:{record.lineno} - {record.getMessage()}"
        )

        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"

        return log_message


def setup_logging() -> logging.Logger:
    """Configure and return the root logger."""
    # Create logger
    logger = logging.getLogger("factguard")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Remove existing handlers
    logger.handlers.clear()

    # Choose formatter based on config
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional - for production)
    if settings.ENVIRONMENT == "production":
        file_handler = logging.FileHandler("factguard.log")
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Initialize logger
logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(f"factguard.{name}")


def log_with_context(
    logger_instance: logging.Logger,
    level: str,
    message: str,
    **extra_fields: Any,
) -> None:
    """Log a message with additional context fields."""
    log_func = getattr(logger_instance, level.lower())
    record = logger_instance.makeRecord(
        logger_instance.name,
        getattr(logging, level),
        "n/a",
        0,
        message,
        (),
        None,
    )
    record.extra_fields = extra_fields
    log_func(record)
