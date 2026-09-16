"""Major Incident Intelligence & Governance (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    HighRiskOperationRequiresApprovalException,
)


class MajorIncidentStatus(str, Enum):
    DECLARED = "DECLARED"
    INVESTIGATING = "INVESTIGATING"
    STAKEHOLDERS_NOTIFIED = "STAKEHOLDERS_NOTIFIED"
    RESOLVED = "RESOLVED"
    CONCLUDED = "CONCLUDED"


class MajorIncidentImpact(str, Enum):
    CRITICAL_BUSINESS_HALT = "CRITICAL_BUSINESS_HALT"
    REVENUE_IMPACT = "REVENUE_IMPACT"
    COMPLIANCE_BREACH = "COMPLIANCE_BREACH"
    REGIONAL_OUTAGE = "REGIONAL_OUTAGE"


class MajorIncident(BaseModel):
    major_incident_id: str = Field(default_factory=lambda: f"maj_inc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    title: str
    impact: MajorIncidentImpact = MajorIncidentImpact.CRITICAL_BUSINESS_HALT
    status: MajorIncidentStatus = MajorIncidentStatus.DECLARED
    requires_human_oversight: bool = True
    approval_id: Optional[str] = None
    declared_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


class MajorIncidentManager:
    """Manages major incident declaration and escalation requiring human oversight."""

    def __init__(self) -> None:
        self._major_incidents: Dict[str, MajorIncident] = {}

    def declare_major_incident(
        self,
        tenant_id: str,
        incident_id: str,
        title: str,
        impact: MajorIncidentImpact = MajorIncidentImpact.CRITICAL_BUSINESS_HALT,
    ) -> MajorIncident:
        maj = MajorIncident(
            tenant_id=tenant_id,
            incident_id=incident_id,
            title=title,
            impact=impact,
            requires_human_oversight=True,
        )
        self._major_incidents[maj.major_incident_id] = maj
        return maj

    def approve_major_incident_resolution(
        self, tenant_id: str, major_incident_id: str, approval_id: str = "appr_maj_123"
    ) -> MajorIncident:
        maj = self.get_major_incident(tenant_id, major_incident_id)
        maj.approval_id = approval_id
        maj.status = MajorIncidentStatus.RESOLVED
        maj.resolved_at = datetime.now(timezone.utc)
        return maj

    def resolve_major_incident(self, tenant_id: str, major_incident_id: str) -> MajorIncident:
        maj = self.get_major_incident(tenant_id, major_incident_id)
        if maj.requires_human_oversight and not maj.approval_id:
            raise HighRiskOperationRequiresApprovalException("RESOLVE_MAJOR_INCIDENT", 95.0)
        maj.status = MajorIncidentStatus.RESOLVED
        maj.resolved_at = datetime.now(timezone.utc)
        return maj

    def get_major_incident(self, tenant_id: str, major_incident_id: str) -> MajorIncident:
        maj = self._major_incidents.get(major_incident_id)
        if not maj or maj.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return maj
