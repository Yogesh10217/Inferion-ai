"""Identity Investigations."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException
from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot


class IdentityFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: str = "MEDIUM"
    description: str
    recommendation: str = ""


class IdentityInvestigationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    source: str = "identity_logs"


class IdentityInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    status: str = "OPEN"  # OPEN, INVESTIGATING, CONCLUDED, CLOSED
    findings: List[IdentityFinding] = Field(default_factory=list)
    evidence: List[IdentityInvestigationEvidence] = Field(default_factory=list)
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityInvestigationManager:
    """Manages identity investigations and generates platform snapshots upon conclusion."""

    def __init__(self, snapshot_factory: Optional[SnapshotFactory] = None) -> None:
        self.snapshot_factory = snapshot_factory or SnapshotFactory()
        self._investigations: Dict[str, IdentityInvestigation] = {}

    def create_investigation(
        self,
        tenant_id: str,
        identity_id: str,
    ) -> IdentityInvestigation:
        inv = IdentityInvestigation(
            tenant_id=tenant_id,
            identity_id=identity_id,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def conclude_investigation(
        self,
        tenant_id: str,
        investigation_id: str,
        findings: List[IdentityFinding],
    ) -> PlatformSnapshot:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()

        inv.findings = findings
        inv.status = "CONCLUDED"

        snapshot = self.snapshot_factory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="IDENTITY",
            resource_id=inv.identity_id,
            domain_payload={
                "investigation_id": inv.investigation_id,
                "findings": [f.model_dump() for f in findings],
                "status": inv.status,
            },
        )
        inv.snapshot_id = snapshot.metadata.snapshot_id
        return snapshot

    def get_investigation(self, tenant_id: str, investigation_id: str) -> IdentityInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return inv
