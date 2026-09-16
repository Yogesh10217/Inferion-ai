"""Continuous Control Signal Collection Subsystem (Phase 5.38)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.platform_contracts.tenant import TenantAccessGuard


class ControlSignalType(str, Enum):
    RELIABILITY = "RELIABILITY"
    SECURITY = "SECURITY"
    EVENT = "EVENT"
    RESILIENCE = "RESILIENCE"
    AI_LIFECYCLE = "AI_LIFECYCLE"
    AGENT_RUNTIME = "AGENT_RUNTIME"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    COMPLIANCE = "COMPLIANCE"


class ControlSignalSource(str, Enum):
    EVENT_INTELLIGENCE = "EVENT_INTELLIGENCE"
    RELIABILITY_PLATFORM = "RELIABILITY_PLATFORM"
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"
    PLATFORM_RESILIENCE = "PLATFORM_RESILIENCE"
    AI_LIFECYCLE_PLATFORM = "AI_LIFECYCLE_PLATFORM"
    AGENT_ORCHESTRATION = "AGENT_ORCHESTRATION"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    COMPLIANCE_PLATFORM = "COMPLIANCE_PLATFORM"


class ControlSignalSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ControlSignalReference(BaseModel):
    source: ControlSignalSource
    source_event_id: str
    source_resource_id: str


class ControlSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    signal_type: ControlSignalType
    source: ControlSignalSource
    severity: ControlSignalSeverity = ControlSignalSeverity.INFO
    reference: ControlSignalReference
    payload: Dict[str, Any] = Field(default_factory=dict)
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlSignalManager:
    """Collects and sanitizes continuous control signals from across the enterprise platform."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.sanitizer = SensitiveDataSanitizer()
        self._signals: Dict[str, ControlSignal] = {}

    def collect_signal(
        self,
        tenant_id: str,
        signal_type: ControlSignalType,
        source: ControlSignalSource,
        source_event_id: str,
        source_resource_id: str,
        severity: ControlSignalSeverity = ControlSignalSeverity.INFO,
        raw_payload: Optional[Dict[str, Any]] = None,
    ) -> ControlSignal:
        payload = raw_payload or {}
        sanitized = self.sanitizer.sanitize_copy(payload)

        sig = ControlSignal(
            tenant_id=tenant_id,
            signal_type=signal_type,
            source=source,
            severity=severity,
            reference=ControlSignalReference(
                source=source,
                source_event_id=source_event_id,
                source_resource_id=source_resource_id,
            ),
            payload=payload,
            sanitized_payload=sanitized,
        )
        self._signals[sig.signal_id] = sig
        return sig

    def list_signals(self, tenant_id: str, signal_type: Optional[ControlSignalType] = None) -> List[ControlSignal]:
        res = []
        for sig in self._signals.values():
            if sig.tenant_id == tenant_id or tenant_id == "global":
                if signal_type and sig.signal_type != signal_type:
                    continue
                res.append(sig)
        return res
