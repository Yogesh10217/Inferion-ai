"""Assurance Violation Lifecycle Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import (
    AssuranceViolationNotFoundException,
    InvalidControlTransitionException,
    ImmutableAssuranceRecordException,
    CrossTenantControlAssuranceAccessException,
)


class ViolationSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ViolationStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    REMEDIATION_DELEGATED = "REMEDIATION_DELEGATED"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class ViolationImpact(BaseModel):
    impact_score: float = 8.5
    affected_components: List[str] = Field(default_factory=list)
    risk_level: str = "HIGH"


class ViolationFinding(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ControlViolation(BaseModel):
    violation_id: str = Field(default_factory=lambda: f"viol_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    severity: ViolationSeverity = ViolationSeverity.HIGH
    status: ViolationStatus = ViolationStatus.DETECTED
    finding: ViolationFinding
    impact: ViolationImpact = Field(default_factory=ViolationImpact)
    remediation_plan_id: Optional[str] = None
    is_closed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlViolationManager:
    """Manages control violations lifecycle and transitions."""

    VALID_TRANSITIONS: Dict[ViolationStatus, List[ViolationStatus]] = {
        ViolationStatus.DETECTED: [ViolationStatus.TRIAGED, ViolationStatus.INVESTIGATING, ViolationStatus.REMEDIATION_PLANNED],
        ViolationStatus.TRIAGED: [ViolationStatus.INVESTIGATING, ViolationStatus.REMEDIATION_PLANNED],
        ViolationStatus.INVESTIGATING: [ViolationStatus.REMEDIATION_PLANNED, ViolationStatus.REMEDIATION_DELEGATED],
        ViolationStatus.REMEDIATION_PLANNED: [ViolationStatus.REMEDIATION_DELEGATED],
        ViolationStatus.REMEDIATION_DELEGATED: [ViolationStatus.VERIFYING],
        ViolationStatus.VERIFYING: [ViolationStatus.RESOLVED, ViolationStatus.REMEDIATION_PLANNED],
        ViolationStatus.RESOLVED: [ViolationStatus.CLOSED],
        ViolationStatus.CLOSED: [],
    }

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._violations: Dict[str, ControlViolation] = {}

    def create_violation(
        self,
        tenant_id: str,
        control_id: str,
        severity: ViolationSeverity,
        finding_code: str,
        message: str,
    ) -> ControlViolation:
        viol = ControlViolation(
            tenant_id=tenant_id,
            control_id=control_id,
            severity=severity,
            status=ViolationStatus.DETECTED,
            finding=ViolationFinding(code=finding_code, message=message),
        )
        self._violations[viol.violation_id] = viol
        return viol

    def transition_status(self, violation_id: str, tenant_id: str, target_status: ViolationStatus) -> ControlViolation:
        viol = self.get_violation(violation_id, tenant_id)

        if viol.is_closed:
            raise ImmutableAssuranceRecordException(f"Violation '{violation_id}' is closed and immutable.")

        allowed = self.VALID_TRANSITIONS.get(viol.status, [])
        if target_status not in allowed:
            raise InvalidControlTransitionException(viol.status.value, target_status.value)

        viol.status = target_status
        if target_status == ViolationStatus.CLOSED:
            viol.is_closed = True
        viol.updated_at = datetime.now(timezone.utc)
        return viol

    def get_violation(self, violation_id: str, tenant_id: str) -> ControlViolation:
        v = self._violations.get(violation_id)
        if not v:
            raise AssuranceViolationNotFoundException(violation_id)
        try:
            self.tenant_guard.enforce_isolation(tenant_id, v.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()
        return v
