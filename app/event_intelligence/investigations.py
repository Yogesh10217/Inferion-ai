"""Cross-Platform Investigation Subsystem (Phase 5.34)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot
from app.event_intelligence.exceptions import CrossTenantEventAccessException


class InvestigationStatus(str, Enum):
    INITIATED = "INITIATED"
    INVESTIGATING = "INVESTIGATING"
    CONCLUDED = "CONCLUDED"
    CLOSED = "CLOSED"


class InvestigationFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"fnd_{uuid.uuid4().hex[:12]}")
    title: str
    description: str


class InvestigationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"invevid_{uuid.uuid4().hex[:12]}")
    source_subsystem: str
    reference_id: str


class InvestigationConclusion(BaseModel):
    summary: str
    recommended_action: str


class EventInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    event_id: str
    status: InvestigationStatus = InvestigationStatus.INITIATED
    findings: List[InvestigationFinding] = Field(default_factory=list)
    evidences: List[InvestigationEvidence] = Field(default_factory=list)
    conclusion: Optional[InvestigationConclusion] = None
    snapshot: Optional[PlatformSnapshot] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventInvestigationManager:
    """Manages cross-platform investigations and generates immutable snapshots on conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, EventInvestigation] = {}

    def initiate_investigation(self, tenant_id: str, event_id: str) -> EventInvestigation:
        inv = EventInvestigation(tenant_id=tenant_id, event_id=event_id, status=InvestigationStatus.INVESTIGATING)
        self._investigations[inv.investigation_id] = inv
        return inv

    def conclude_investigation(
        self,
        investigation_id: str,
        tenant_id: str,
        summary: str,
        recommended_action: str = "REQUEST_SECURITY_REMEDIATION",
    ) -> EventInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv:
            raise KeyError(f"Investigation '{investigation_id}' not found.")
        if tenant_id != "global" and inv.tenant_id != "global" and tenant_id != inv.tenant_id:
            raise CrossTenantEventAccessException(tenant_id, inv.tenant_id)

        inv.conclusion = InvestigationConclusion(summary=summary, recommended_action=recommended_action)
        inv.status = InvestigationStatus.CONCLUDED

        snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="EVENT_INVESTIGATION",
            resource_id=investigation_id,
            domain_payload=inv.model_dump(exclude={"snapshot"}),
        )
        inv.snapshot = snap
        return inv
