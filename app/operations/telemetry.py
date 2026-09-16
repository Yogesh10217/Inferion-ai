"""Unified Telemetry Platform with Trace/Execution Correlation & Secret Redaction."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TelemetryType(str, Enum):
    METRIC = "METRIC"
    LOG = "LOG"
    TRACE = "TRACE"
    EVENT = "EVENT"
    HEALTH = "HEALTH"
    AUDIT = "AUDIT"
    SECURITY = "SECURITY"
    COST = "COST"
    QUALITY = "QUALITY"
    DRIFT = "DRIFT"
    ANOMALY = "ANOMALY"
    INCIDENT = "INCIDENT"


class TelemetrySeverity(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TelemetryContext(BaseModel):
    platform: str = "llm-inference-engine"
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    resource_id: Optional[str] = None
    execution_id: Optional[str] = None
    trace_id: Optional[str] = None
    request_id: Optional[str] = None


class TelemetryEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"tel_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=_now)

    telemetry_type: TelemetryType = TelemetryType.EVENT
    severity: TelemetrySeverity = TelemetrySeverity.INFO

    source_service: str
    context: TelemetryContext = Field(default_factory=TelemetryContext)
    message: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("message", mode="before")
    @classmethod
    def sanitize_message(cls, v: Any) -> str:
        s = str(v)
        secret_mgr = SecretManager()
        return secret_mgr.sanitize_text(s) if hasattr(secret_mgr, "sanitize_text") else s


class TelemetryManager:
    """Ingests, correlates, and queries multi-tenant telemetry events with automated secret redaction."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._events: List[TelemetryEvent] = []

    def record_event(
        self,
        source_service: str,
        telemetry_type: TelemetryType,
        message: str,
        severity: TelemetrySeverity = TelemetrySeverity.INFO,
        context: Optional[TelemetryContext] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> TelemetryEvent:
        ctx = context or TelemetryContext()
        # Redact payload if secret_manager supports masking
        clean_payload = payload or {}
        if hasattr(self.secret_manager, "redact_dict"):
            clean_payload = self.secret_manager.redact_dict(clean_payload)

        evt = TelemetryEvent(
            source_service=source_service,
            telemetry_type=telemetry_type,
            severity=severity,
            context=ctx,
            message=message,
            payload=clean_payload,
        )
        self._events.append(evt)
        logger.debug(f"[TELEMETRY] Recorded event '{evt.event_id}' ({telemetry_type.value}/{severity.value}): {evt.message}")
        return evt

    def list_events(
        self,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        telemetry_type: Optional[TelemetryType] = None,
    ) -> List[TelemetryEvent]:
        res = self._events
        if tenant_id:
            res = [e for e in res if e.context.tenant_id == tenant_id]
        if trace_id:
            res = [e for e in res if e.context.trace_id == trace_id]
        if execution_id:
            res = [e for e in res if e.context.execution_id == execution_id]
        if telemetry_type:
            res = [e for e in res if e.telemetry_type == telemetry_type]
        return res
