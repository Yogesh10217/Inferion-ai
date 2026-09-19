"""Structured Logging Platform with automatic secret redaction."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

from app.observability.context import get_current_context

# Sensitive key patterns for automatic secret redaction
SECRET_KEY_PATTERNS = [
    re.compile(r".*api[_-]?key.*", re.IGNORECASE),
    re.compile(r".*secret.*", re.IGNORECASE),
    re.compile(r".*token.*", re.IGNORECASE),
    re.compile(r".*password.*", re.IGNORECASE),
    re.compile(r".*authorization.*", re.IGNORECASE),
    re.compile(r".*auth[_-]?header.*", re.IGNORECASE),
    re.compile(r".*bearer.*", re.IGNORECASE),
    re.compile(r".*private[_-]?key.*", re.IGNORECASE),
    re.compile(r".*credential.*", re.IGNORECASE),
]

REDACTED_TEXT = "[REDACTED]"


def sanitize_value(key: str, value: Any) -> Any:
    """Recursively sanitize sensitive key-value pairs."""
    if isinstance(key, str):
        for pattern in SECRET_KEY_PATTERNS:
            if pattern.match(key):
                return REDACTED_TEXT

    if isinstance(value, dict):
        return {k: sanitize_value(k, v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_value(key, item) for item in value]
    elif isinstance(value, str):
        # Check if the string value contains a raw JWT or Bearer token
        if value.lower().startswith("bearer ") or "eyJ" in value:
            if len(value) > 20 and "." in value:
                return REDACTED_TEXT
    return value


class StructuredLogger:
    """Enterprise Structured Logger that formats log events with contextual attributes and redacts secrets."""

    def __init__(self, service_name: str = "llm-inference-engine", component: str = "general") -> None:
        self.service_name = service_name
        self.component = component
        self._logger = logging.getLogger(f"observability.{component}")

    def _format_event(
        self,
        level: str,
        message: str,
        event_type: Optional[str] = None,
        duration: Optional[float] = None,
        error_type: Optional[str] = None,
        tool_name: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Construct structured payload populated with context and sanitized extras."""
        ctx = get_current_context()
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()

        payload: Dict[str, Any] = {
            "timestamp": now,
            "level": level,
            "service": self.service_name,
            "component": self.component,
            "message": message,
            "trace_id": ctx.trace_id,
            "span_id": ctx.span_id,
            "execution_id": ctx.execution_id,
            "tenant_id": ctx.tenant_id,
            "workspace_id": ctx.workspace_id,
            "agent_id": ctx.agent_id,
            "workflow_id": ctx.workflow_id,
            "tool_name": tool_name or ctx.tool_execution_id,
            "event_type": event_type or "general",
            "duration": duration,
            "error_type": error_type,
        }

        # Filter out None values
        payload = {k: v for k, v in payload.items() if v is not None}

        if extra:
            sanitized_extra = {k: sanitize_value(k, v) for k, v in extra.items()}
            payload["attributes"] = sanitized_extra

        return payload

    def log(
        self,
        level: str,
        message: str,
        event_type: Optional[str] = None,
        duration: Optional[float] = None,
        error_type: Optional[str] = None,
        tool_name: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format and emit a structured log record."""
        payload = self._format_event(
            level=level.upper(),
            message=message,
            event_type=event_type,
            duration=duration,
            error_type=error_type,
            tool_name=tool_name,
            extra=extra,
        )

        formatted_json = json.dumps(payload)

        lvl_upper = level.upper()
        if lvl_upper == "DEBUG":
            self._logger.debug(formatted_json)
        elif lvl_upper == "INFO":
            self._logger.info(formatted_json)
        elif lvl_upper == "WARNING" or lvl_upper == "WARN":
            self._logger.warning(formatted_json)
        elif lvl_upper == "ERROR":
            self._logger.error(formatted_json)
        elif lvl_upper == "CRITICAL":
            self._logger.critical(formatted_json)
        else:
            self._logger.info(formatted_json)

        return payload

    def debug(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> Dict[str, Any]:
        return self.log("CRITICAL", message, **kwargs)
