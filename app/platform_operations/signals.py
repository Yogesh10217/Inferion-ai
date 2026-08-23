"""Operational Signal Ingestion, Normalization, & Sanitization Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SignalSource(str, Enum):
    METRICS = "METRICS"
    LOGS = "LOGS"
    TRACES = "TRACES"
    APPLICATION_RUNTIME = "APPLICATION_RUNTIME"
    DEPLOYMENT = "DEPLOYMENT"
    WORKFLOW = "WORKFLOW"
    AGENT = "AGENT"
    INTEGRATION = "INTEGRATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    SECURITY = "SECURITY"
    GOVERNANCE = "GOVERNANCE"
    FINOPS = "FINOPS"


class SignalSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SignalType(str, Enum):
    METRIC_THRESHOLD = "METRIC_THRESHOLD"
    LOG_ERROR = "LOG_ERROR"
    TRACE_ANOMALY = "TRACE_ANOMALY"
    RUNTIME_DEGRADATION = "RUNTIME_DEGRADATION"
    DEPLOYMENT_EVENT = "DEPLOYMENT_EVENT"
    WORKFLOW_FAILURE = "WORKFLOW_FAILURE"
    AGENT_TOOL_FAILURE = "AGENT_TOOL_FAILURE"
    INTEGRATION_TIMEOUT = "INTEGRATION_TIMEOUT"
    SECURITY_ALERT = "SECURITY_ALERT"
    GOVERNANCE_VIOLATION = "GOVERNANCE_VIOLATION"
    COST_ANOMALY = "COST_ANOMALY"


class OperationalSignal(BaseModel):
    """Normalized operational signal."""
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    tenant_id: str = "global"
    source: SignalSource
    signal_type: SignalType
    severity: SignalSeverity = SignalSeverity.INFO
    service_id: Optional[str] = None
    resource_id: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    message: str
    metrics: Dict[str, float] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class SignalNormalizer:
    """Normalizes raw input signals and sanitizes secret credentials."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()

    def normalize(
        self,
        tenant_id: str,
        source: SignalSource,
        signal_type: SignalType,
        message: str,
        severity: SignalSeverity = SignalSeverity.INFO,
        service_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> OperationalSignal:
        # Sanitize message and payload text
        sanitized_msg = self.secret_manager.sanitize_text(message)
        sanitized_payload = self._sanitize_dict(payload or {})

        return OperationalSignal(
            tenant_id=tenant_id,
            source=source,
            signal_type=signal_type,
            severity=severity,
            service_id=service_id,
            resource_id=resource_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            message=sanitized_msg,
            metrics=metrics or {},
            payload=sanitized_payload,
        )

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                result[k] = self.secret_manager.sanitize_text(v)
            elif isinstance(v, dict):
                result[k] = self._sanitize_dict(v)
            else:
                result[k] = v
        return result


class SignalManager:
    """Stores and indexes operational signals with tenant isolation."""

    def __init__(self, normalizer: Optional[SignalNormalizer] = None) -> None:
        self.normalizer = normalizer or SignalNormalizer()
        self._signals: Dict[str, OperationalSignal] = {}

    def ingest_signal(
        self,
        tenant_id: str,
        source: SignalSource,
        signal_type: SignalType,
        message: str,
        severity: SignalSeverity = SignalSeverity.INFO,
        service_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> OperationalSignal:
        signal = self.normalizer.normalize(
            tenant_id=tenant_id,
            source=source,
            signal_type=signal_type,
            message=message,
            severity=severity,
            service_id=service_id,
            resource_id=resource_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            metrics=metrics,
            payload=payload,
        )
        self._signals[signal.signal_id] = signal
        logger.info(f"[SIGNAL MANAGER] Ingested signal {signal.signal_id} [{signal.severity.value}] for tenant {tenant_id}")
        return signal

    def list_signals(
        self,
        tenant_id: str,
        service_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        severity: Optional[SignalSeverity] = None,
    ) -> List[OperationalSignal]:
        results = [s for s in self._signals.values() if s.tenant_id in (tenant_id, "global")]
        if service_id:
            results = [s for s in results if s.service_id == service_id]
        if correlation_id:
            results = [s for s in results if s.correlation_id == correlation_id]
        if severity:
            results = [s for s in results if s.severity == severity]
        return results
