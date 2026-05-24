import json
import logging
import sys
from datetime import datetime, timezone

from app.config import settings


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"[{timestamp}] {record.levelname:<8} "
            f"{record.name}:{record.funcName}:{record.lineno} - {record.getMessage()}"
        )
        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"
        return log_message


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("factguard")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    logger.handlers.clear()

    formatter = JSONFormatter() if settings.LOG_FORMAT == "json" else TextFormatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if settings.ENVIRONMENT == "production":
        file_handler = logging.FileHandler("factguard.log")
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"factguard.{name}")
