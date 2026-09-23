"""Decision investigation lifecycle producing PlatformSnapshot artifacts upon conclusion."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException
from app.platform_contracts.snapshots import SnapshotFactory


class InvestigationStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FINDINGS_RECORDED = "FINDINGS_RECORDED"
    DECISION_PLANNED = "DECISION_PLANNED"
    CONCLUDED = "CONCLUDED"


class DecisionFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: str = "MEDIUM"
    domain: str = "general"


class InvestigationEvidence(BaseModel):
    source: str
    summary: str
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class DecisionInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    decision_id: str
    title: str
    description: str = ""
    status: InvestigationStatus = InvestigationStatus.OPEN
    findings: List[DecisionFinding] = Field(default_factory=list)
    evidence: List[InvestigationEvidence] = Field(default_factory=list)
    snapshot_reference_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class DecisionInvestigationManager:
    """Manages the full lifecycle of decision investigations."""

    def __init__(self) -> None:
        self._investigations: Dict[str, DecisionInvestigation] = {}

    def create_investigation(
        self,
        tenant_id: str,
        decision_id: str,
        title: str,
        description: str = "",
    ) -> DecisionInvestigation:
        inv = DecisionInvestigation(
            tenant_id=tenant_id,
            decision_id=decision_id,
            title=title,
            description=description,
            status=InvestigationStatus.OPEN,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def get_investigation(self, investigation_id: str, tenant_id: str) -> DecisionInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv:
            raise ValueError(f"Investigation '{investigation_id}' not found")
        if inv.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return inv

    def record_finding(
        self,
        investigation_id: str,
        tenant_id: str,
        title: str,
        description: str,
        severity: str = "MEDIUM",
        domain: str = "general",
    ) -> DecisionInvestigation:
        inv = self.get_investigation(investigation_id, tenant_id)
        inv.findings.append(DecisionFinding(title=title, description=description, severity=severity, domain=domain))
        inv.status = InvestigationStatus.FINDINGS_RECORDED
        inv.updated_at = datetime.now(timezone.utc)
        return inv

    def conclude_investigation(self, investigation_id: str, tenant_id: str) -> DecisionInvestigation:
        inv = self.get_investigation(investigation_id, tenant_id)
        inv.status = InvestigationStatus.CONCLUDED
        inv.concluded_at = datetime.now(timezone.utc)
        inv.updated_at = inv.concluded_at

        # Generate PlatformSnapshot upon conclusion
        snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="DECISION_INVESTIGATION_SNAPSHOT",
            resource_id=inv.investigation_id,
            domain_payload={
                "investigation_id": inv.investigation_id,
                "decision_id": inv.decision_id,
                "status": inv.status.value,
                "findings_count": len(inv.findings),
            },
            extra_metadata={"source": "DecisionInvestigationManager"},
        )
        inv.snapshot_reference_id = snap.snapshot_id
        return inv
