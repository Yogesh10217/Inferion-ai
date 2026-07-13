import json
import logging
import uuid
from datetime import datetime, timezone
from logging.config import dictConfig


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "app": {
                    "handlers": ["console"],
                    "level": level.upper(),
                    "propagate": False,
                }
            },
            "root": {"handlers": ["console"], "level": level.upper()},
        }
    )


def get_logger(name: str = "app") -> logging.Logger:
    """Return a module logger."""
    return logging.getLogger(name)


def log_request_event(
    *,
    method: str = "UNKNOWN",
    endpoint: str,
    latency_ms: float,
    provider: str | None,
    model: str | None,
    status_code: int,
    client_ip: str | None = None,
    request_id: str | None = None,
    level: str = "INFO",
    extra: dict | None = None,
) -> None:
    """Emit a structured JSON log entry for request lifecycle events."""
    logger = get_logger()
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id or str(uuid.uuid4()),
        "method": method,
        "endpoint": endpoint,
        "provider": provider,
        "model": model,
        "latency_ms": round(latency_ms, 3),
        "status_code": status_code,
        "client_ip": client_ip,
    }
    if extra:
        payload.update(extra)
    logger.log(getattr(logging, level.upper(), logging.INFO), json.dumps(payload, ensure_ascii=False))
