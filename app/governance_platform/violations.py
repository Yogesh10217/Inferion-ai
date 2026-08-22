"""AI Incident & Governance Violation Management System."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.operations.incidents import IncidentManager, IncidentSeverity

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ViolationType(str, Enum):
    POLICY_VIOLATION = "POLICY_VIOLATION"
    DATA_VIOLATION = "DATA_VIOLATION"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    MODEL_SAFETY_VIOLATION = "MODEL_SAFETY_VIOLATION"
    BUDGET_VIOLATION = "BUDGET_VIOLATION"
    AUTONOMY_VIOLATION = "AUTONOMY_VIOLATION"
    COMPLIANCE_VIOLATION = "COMPLIANCE_VIOLATION"
    ACCESS_VIOLATION = "ACCESS_VIOLATION"


class ViolationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ViolationStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    ACCEPTED_RISK = "ACCEPTED_RISK"
    CLOSED = "CLOSED"


class GovernanceViolation(BaseModel):
    violation_id: str = Field(default_factory=lambda: f"viol_{uuid.uuid4().hex[:10]}")
    title: str
    tenant_id: str = "global"
    violation_type: ViolationType = ViolationType.POLICY_VIOLATION
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    status: ViolationStatus = ViolationStatus.DETECTED

    primary_resource_id: str = ""
    description: str = ""
    evidence_ids: List[str] = Field(default_factory=list)
    incident_id: Optional[str] = None

    detected_at: datetime = Field(default_factory=_now)
    resolved_at: Optional[datetime] = None


class ViolationManager:
    """Manages governance violations, lifecycle transitions, and automatic operations incident integration."""

    def __init__(self, incident_manager: Optional[IncidentManager] = None) -> None:
        self.incident_manager = incident_manager or IncidentManager()
        self._violations: Dict[str, GovernanceViolation] = {}

    def record_violation(
        self,
        title: str,
        violation_type: ViolationType,
        severity: ViolationSeverity,
        primary_resource_id: str,
        description: str = "",
        tenant_id: str = "global",
        evidence_ids: Optional[List[str]] = None,
    ) -> GovernanceViolation:
        v = GovernanceViolation(
            title=title,
            violation_type=violation_type,
            severity=severity,
            primary_resource_id=primary_resource_id,
            description=description,
            tenant_id=tenant_id,
            evidence_ids=evidence_ids or [],
        )

        # For CRITICAL or HIGH violations, automatically create an Operations Incident
        if severity in (ViolationSeverity.CRITICAL, ViolationSeverity.HIGH):
            op_sev = IncidentSeverity.SEV1_CRITICAL if severity == ViolationSeverity.CRITICAL else IncidentSeverity.SEV2_HIGH
            inc = self.incident_manager.create_incident(
                title=f"[GOVERNANCE VIOLATION] {title}",
                tenant_id=tenant_id,
                severity=op_sev,
                primary_resource_id=primary_resource_id,
            )
            v.incident_id = inc.incident_id
            logger.warning(f"[VIOLATION MANAGER] Created Operations Incident '{inc.incident_id}' for {severity.value} violation '{v.violation_id}'")

        self._violations[v.violation_id] = v
        logger.info(f"[VIOLATION MANAGER] Recorded violation '{v.violation_id}' ({violation_type.value}) for '{primary_resource_id}'")
        return v

    def update_status(self, violation_id: str, status: ViolationStatus) -> GovernanceViolation:
        v = self.get_violation(violation_id)
        v.status = status
        if status in (ViolationStatus.RESOLVED, ViolationStatus.CLOSED):
            v.resolved_at = _now()
        logger.info(f"[VIOLATION MANAGER] Violation '{violation_id}' status updated -> {status.value}")
        return v

    def get_violation(self, violation_id: str) -> GovernanceViolation:
        v = self._violations.get(violation_id)
        if not v:
            raise KeyError(f"Violation '{violation_id}' not found")
        return v

    def list_violations(self, tenant_id: Optional[str] = None) -> List[GovernanceViolation]:
        res = list(self._violations.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
