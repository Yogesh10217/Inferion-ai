"""Investigation Management Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory
from app.security_intelligence.exceptions import CrossTenantSecurityAccessException, ImmutableSecurityRecordException


class InvestigationStatus(str, Enum):
    OPEN = "OPEN"
    COLLECTING_EVIDENCE = "COLLECTING_EVIDENCE"
    ANALYZING = "ANALYZING"
    CONCLUDED = "CONCLUDED"


class InvestigationFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"fnd_{uuid.uuid4().hex[:12]}")
    description: str
    severity: str = "HIGH"


class SecurityInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    title: str
    status: InvestigationStatus = InvestigationStatus.OPEN
    findings: List[InvestigationFinding] = Field(default_factory=list)
    snapshot: Optional[PlatformSnapshot] = None
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(
                resource_id=self.investigation_id,
                tenant_id=self.tenant_id,
            )


class InvestigationManager:
    """Manages security investigations and generates immutable snapshots on conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, SecurityInvestigation] = {}

    def create_investigation(
        self,
        tenant_id: str,
        incident_id: str,
        title: str,
    ) -> SecurityInvestigation:
        inv = SecurityInvestigation(
            tenant_id=tenant_id,
            incident_id=incident_id,
            title=title,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def conclude_investigation(
        self,
        investigation_id: str,
        tenant_id: str,
        findings: List[InvestigationFinding],
    ) -> SecurityInvestigation:
        inv = self.get_investigation(investigation_id, tenant_id)

        if inv.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableSecurityRecordException(investigation_id)

        inv.findings = findings
        inv.status = InvestigationStatus.CONCLUDED

        snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="SECURITY_INVESTIGATION",
            resource_id=inv.investigation_id,
            domain_payload=inv.model_dump(exclude={"snapshot", "immutable_record"}),
        )

        inv.snapshot = snap

        fp = FingerprintGenerator.generate(snap.model_dump())
        ImmutableResourceValidator.finalize(inv.immutable_record, fingerprint=fp)
        return inv

    def get_investigation(self, investigation_id: str, tenant_id: str) -> SecurityInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv:
            raise KeyError(f"Investigation '{investigation_id}' not found.")
        if tenant_id != "global" and inv.tenant_id != "global" and tenant_id != inv.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, inv.tenant_id)
        return inv
