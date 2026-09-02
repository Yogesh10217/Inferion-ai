"""Cross-Platform Access Signal Ingestion (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class AccessSignalType(str, Enum):
    IDENTITY_EVENT = "IDENTITY_EVENT"
    AUTHORIZATION_EVENT = "AUTHORIZATION_EVENT"
    PRIVILEGED_ACTION = "PRIVILEGED_ACTION"
    ANOMALY_SIGNAL = "ANOMALY_SIGNAL"
    AUDIT_EVENT = "AUDIT_EVENT"


class AccessSignalSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccessSignalSource(str, Enum):
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"
    EVENT_INTELLIGENCE = "EVENT_INTELLIGENCE"
    CONTROL_ASSURANCE = "CONTROL_ASSURANCE"
    IDENTITY_SECURITY = "IDENTITY_SECURITY"


class AccessSignal(BaseModel):
    """Sanitized access telemetry signal."""
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    signal_type: AccessSignalType
    severity: AccessSignalSeverity = AccessSignalSeverity.INFO
    source: AccessSignalSource = AccessSignalSource.SECURITY_INTELLIGENCE
    source_telemetry_ref: str
    subject_identity_id: str
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessSignalManager:
    """Ingests and sanitizes cross-platform access signals."""

    def __init__(self) -> None:
        self._signals: Dict[str, AccessSignal] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def ingest_signal(
        self,
        tenant_id: str,
        signal_type: AccessSignalType,
        source_telemetry_ref: str,
        subject_identity_id: str,
        severity: AccessSignalSeverity = AccessSignalSeverity.INFO,
        source: AccessSignalSource = AccessSignalSource.SECURITY_INTELLIGENCE,
        raw_metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessSignal:
        sanitized = self.sanitizer.sanitize(raw_metadata or {})
        sig = AccessSignal(
            tenant_id=tenant_id,
            signal_type=signal_type,
            severity=severity,
            source=source,
            source_telemetry_ref=source_telemetry_ref,
            subject_identity_id=subject_identity_id,
            sanitized_metadata=sanitized,
        )
        self._signals[sig.signal_id] = sig
        return sig

    def get_signal(self, tenant_id: str, signal_id: str) -> AccessSignal:
        sig = self._signals.get(signal_id)
        if not sig or sig.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return sig

    def list_signals(self, tenant_id: str, signal_type: Optional[AccessSignalType] = None) -> List[AccessSignal]:
        results = [s for s in self._signals.values() if s.tenant_id == tenant_id]
        if signal_type:
            results = [s for s in results if s.signal_type == signal_type]
        return results
