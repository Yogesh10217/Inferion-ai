"""Continuous Compliance Monitoring & Signal Engine."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ComplianceSignalType(str, Enum):
    CONTROL_FAILURE = "CONTROL_FAILURE"
    EVIDENCE_EXPIRED = "EVIDENCE_EXPIRED"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    POLICY_CHANGED = "POLICY_CHANGED"
    ARCHITECTURE_DRIFT = "ARCHITECTURE_DRIFT"
    DATA_GOVERNANCE_VIOLATION = "DATA_GOVERNANCE_VIOLATION"
    SECURITY_EVENT = "SECURITY_EVENT"
    INCIDENT = "INCIDENT"
    DEPLOYMENT_CHANGE = "DEPLOYMENT_CHANGE"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    ATTESTATION_EXPIRED = "ATTESTATION_EXPIRED"
    TRUST_DEGRADATION = "TRUST_DEGRADATION"


class ComplianceSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    signal_type: ComplianceSignalType
    source_system: str
    subject_id: str
    severity: str = "HIGH"
    details: Dict[str, Any] = Field(default_factory=dict)
    emitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceMonitoringRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    signal_type: ComplianceSignalType
    auto_trigger_assessment: bool = True


class ComplianceMonitoringManager:
    """Listens for continuous compliance signals and triggers automated re-assessments or findings."""

    def __init__(self) -> None:
        self._signals: Dict[str, List[ComplianceSignal]] = {}

    def emit_signal(
        self,
        tenant_id: str,
        signal_type: ComplianceSignalType,
        source_system: str,
        subject_id: str,
        severity: str = "HIGH",
        details: Optional[Dict[str, Any]] = None,
    ) -> ComplianceSignal:
        sig = ComplianceSignal(
            tenant_id=tenant_id,
            signal_type=signal_type,
            source_system=source_system,
            subject_id=subject_id,
            severity=severity,
            details=details or {},
        )
        if tenant_id not in self._signals:
            self._signals[tenant_id] = []
        self._signals[tenant_id].append(sig)
        return sig

    def list_signals(self, tenant_id: str) -> List[ComplianceSignal]:
        return self._signals.get(tenant_id, [])
