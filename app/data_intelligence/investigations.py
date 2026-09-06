"""Data investigation intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException
from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot


class InvestigationStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FINDINGS_RECORDED = "FINDINGS_RECORDED"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    CONCLUDED = "CONCLUDED"


class DataFinding(BaseModel):
    finding_id: str
    title: str
    description: str
    root_cause: str
    severity: str = "HIGH"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationEvidence(BaseModel):
    evidence_id: str
    source: str
    details: Dict[str, Any] = Field(default_factory=dict)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataInvestigation(BaseModel):
    investigation_id: str
    incident_id: str
    tenant_id: str
    dataset_id: str
    status: InvestigationStatus = InvestigationStatus.OPEN
    findings: List[DataFinding] = Field(default_factory=list)
    evidence: List[InvestigationEvidence] = Field(default_factory=list)
    concluded_snapshot: Optional[PlatformSnapshot] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class DataInvestigationManager:
    """Manages data investigations and generates PlatformSnapshot upon conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, DataInvestigation] = {}

    def start_investigation(
        self,
        incident_id: str,
        tenant_id: str,
        dataset_id: str,
        investigation_id: Optional[str] = None,
    ) -> DataInvestigation:
        invid = investigation_id or f"dinv-{uuid.uuid4().hex[:8]}"
        inv = DataInvestigation(
            investigation_id=invid,
            incident_id=incident_id,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            status=InvestigationStatus.OPEN,
        )
        self._investigations[invid] = inv
        return inv

    def add_finding(
        self,
        investigation_id: str,
        tenant_id: str,
        title: str,
        description: str,
        root_cause: str,
    ) -> DataFinding:
        inv = self.get_investigation(investigation_id, tenant_id)
        fid = f"find-{uuid.uuid4().hex[:8]}"

        finding = DataFinding(
            finding_id=fid,
            title=title,
            description=description,
            root_cause=root_cause,
        )
        inv.findings.append(finding)
        inv.status = InvestigationStatus.FINDINGS_RECORDED
        return finding

    def conclude_investigation(
        self,
        investigation_id: str,
        tenant_id: str,
    ) -> DataInvestigation:
        inv = self.get_investigation(investigation_id, tenant_id)
        inv.status = InvestigationStatus.CONCLUDED
        inv.concluded_at = datetime.now(timezone.utc)

        # Generate PlatformSnapshot upon conclusion
        snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="DATA_INVESTIGATION",
            resource_id=investigation_id,
            domain_payload={
                "investigation_id": inv.investigation_id,
                "incident_id": inv.incident_id,
                "dataset_id": inv.dataset_id,
                "findings_count": len(inv.findings),
                "status": inv.status.value,
            },
        )
        inv.concluded_snapshot = snap
        return inv

    def get_investigation(self, investigation_id: str, tenant_id: str) -> DataInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv:
            raise Exception(f"Investigation '{investigation_id}' not found.")
        if inv.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return inv
