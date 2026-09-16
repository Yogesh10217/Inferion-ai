"""Security Investigation Management Engine."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.security_assurance.exceptions import (
    CrossTenantSecurityAssuranceException,
    SecurityInvestigationNotFoundException,
)


class SecurityInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"sec-inv-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    incident_id: str
    lead_investigator: str = "security-agent"
    status: str = "OPEN"  # OPEN, IN_PROGRESS, CONCLUDED
    findings: List[str] = Field(default_factory=list)
    root_cause_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityInvestigationManager:
    """Manages forensic security investigations for security incidents."""

    def __init__(self) -> None:
        self._investigations: Dict[str, SecurityInvestigation] = {}

    def launch_investigation(self, tenant_id: str, incident_id: str, lead_investigator: str = "security-agent") -> SecurityInvestigation:
        inv = SecurityInvestigation(
            tenant_id=tenant_id,
            incident_id=incident_id,
            lead_investigator=lead_investigator,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def get_investigation(self, tenant_id: str, investigation_id: str) -> SecurityInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv:
            raise SecurityInvestigationNotFoundException(f"Investigation '{investigation_id}' not found.")
        if inv.tenant_id != tenant_id:
            raise CrossTenantSecurityAssuranceException(f"Tenant '{tenant_id}' cannot access investigation for tenant '{inv.tenant_id}'.")
        return inv

    def add_finding(self, tenant_id: str, investigation_id: str, finding: str) -> SecurityInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        inv.findings.append(finding)
        return inv

    def list_investigations(self, tenant_id: str) -> List[SecurityInvestigation]:
        return [i for i in self._investigations.values() if i.tenant_id == tenant_id]
