from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.deployment.configuration_fingerprint import ConfigurationFingerprintEngine


class DeploymentStructuredFormatter(logging.Formatter):
    """JSON structured log formatter ensuring telemetry context and zero secret leakage."""

    def __init__(self, environment: str, service: str) -> None:
        super().__init__()
        self.environment = environment
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "environment": self.environment,
            "service": self.service,
            "component": getattr(record, "component", record.name),
            "event_type": getattr(record, "event_type", "LOG_EVENT"),
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "correlation_id": getattr(record, "correlation_id", None),
            "tenant_id": getattr(record, "tenant_id", None),
        }

        extra_data = getattr(record, "extra_data", None)
        if isinstance(extra_data, dict):
            log_entry["extra"] = ConfigurationFingerprintEngine.sanitize_dict(extra_data)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps({k: v for k, v in log_entry.items() if v is not None})


class StructuredLoggingConfigurator:
    """Configures structured deployment logging for production services."""

    @classmethod
    def configure_logging(
        cls,
        environment: str,
        service: str = "Enterprise-AI-Platform",
        log_level: str = "INFO",
    ) -> None:
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Clear existing handlers
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

        handler = logging.StreamHandler()
        handler.setFormatter(DeploymentStructuredFormatter(environment=environment, service=service))
        root_logger.addHandler(handler)

    @classmethod
    def log_event(
        cls,
        logger: logging.Logger,
        level: int,
        event_type: str,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        extra = {
            "event_type": event_type,
            "extra_data": extra_data or {},
            "trace_id": trace_id,
            "correlation_id": correlation_id,
        }
        logger.log(level, message, extra=extra)
