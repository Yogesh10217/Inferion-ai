"""Operational investigation lifecycle generating PlatformSnapshots upon conclusion."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException
from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot


class OperationalFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: str = "HIGH"
    description: str
    recommendation: str = ""


class OperationalInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    status: str = "OPEN"  # OPEN, INVESTIGATING, CONCLUDED, CLOSED
    findings: List[OperationalFinding] = Field(default_factory=list)
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalInvestigationManager:
    """Manages operational investigations and produces platform snapshots upon conclusion."""

    def __init__(self, snapshot_factory: Optional[SnapshotFactory] = None) -> None:
        self.snapshot_factory = snapshot_factory or SnapshotFactory()
        self._investigations: Dict[str, OperationalInvestigation] = {}

    def create_investigation(
        self,
        tenant_id: str,
        service_id: str,
    ) -> OperationalInvestigation:
        inv = OperationalInvestigation(
            tenant_id=tenant_id,
            service_id=service_id,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def conclude_investigation(
        self,
        tenant_id: str,
        investigation_id: str,
        findings: List[OperationalFinding],
    ) -> PlatformSnapshot:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantOperationsAssuranceException("Access denied.")

        inv.findings = findings
        inv.status = "CONCLUDED"

        snapshot = self.snapshot_factory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="OPERATIONAL_INVESTIGATION",
            resource_id=inv.service_id,
            domain_payload={
                "investigation_id": inv.investigation_id,
                "service_id": inv.service_id,
                "findings": [f.model_dump() for f in findings],
                "status": inv.status,
            },
        )
        inv.snapshot_id = snapshot.metadata.snapshot_id
        return snapshot

    def get_investigation(self, tenant_id: str, investigation_id: str) -> OperationalInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantOperationsAssuranceException("Access denied.")
        return inv
