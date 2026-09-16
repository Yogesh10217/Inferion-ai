"""Operational Signal Processing Subsystem (Phase 5.31)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class SignalSource(str, Enum):
    TELEMETRY = "TELEMETRY"
    LOGS = "LOGS"
    METRICS = "METRICS"
    TRACES = "TRACES"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    MODEL_MONITOR = "MODEL_MONITOR"
    AGENT_MONITOR = "AGENT_MONITOR"


class SignalSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ReliabilitySignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    source: SignalSource
    severity: SignalSeverity
    metric_name: str
    observed_value: float
    threshold: float
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SignalProcessor:
    """Consumes operational signals without duplicating underlying monitoring storage."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()

    def process_signal(
        self,
        tenant_id: str,
        service_id: str,
        metric_name: str,
        observed_value: float,
        threshold: float,
        source: SignalSource = SignalSource.METRICS,
        severity: SignalSeverity = SignalSeverity.WARNING,
        payload: Optional[Dict[str, Any]] = None,
    ) -> ReliabilitySignal:
        sanitized_payload = self.sanitizer.sanitize_copy(payload or {})
        return ReliabilitySignal(
            tenant_id=tenant_id,
            service_id=service_id,
            source=source,
            severity=severity,
            metric_name=metric_name,
            observed_value=observed_value,
            threshold=threshold,
            payload=sanitized_payload,
        )
