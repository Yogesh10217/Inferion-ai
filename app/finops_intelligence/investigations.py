"""Financial Investigation Lifecycle & Snapshot Generation (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import (
    CrossTenantFinOpsIntelligenceException,
    ImmutableFinOpsRecordException,
)
from app.platform_contracts.snapshots import SnapshotFactory


class FinOpsInvestigationStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FINDINGS_RECORDED = "FINDINGS_RECORDED"
    OPTIMIZATION_PLANNED = "OPTIMIZATION_PLANNED"
    CONCLUDED = "CONCLUDED"


class FinOpsInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"inv_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    target_anomaly_id: Optional[str] = None
    status: FinOpsInvestigationStatus = FinOpsInvestigationStatus.OPEN
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    is_concluded: bool = False
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class FinOpsInvestigationManager:
    """Manages financial investigation lifecycle and generates PlatformSnapshot upon conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, FinOpsInvestigation] = {}

    def open_investigation(
        self, tenant_id: str, title: str, target_anomaly_id: Optional[str] = None
    ) -> FinOpsInvestigation:
        inv = FinOpsInvestigation(
            tenant_id=tenant_id,
            title=title,
            target_anomaly_id=target_anomaly_id,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def start_investigating(self, tenant_id: str, investigation_id: str) -> FinOpsInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        inv.status = FinOpsInvestigationStatus.INVESTIGATING
        return inv

    def record_finding(
        self, tenant_id: str, investigation_id: str, summary: str, details: Optional[Dict[str, Any]] = None
    ) -> FinOpsInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.is_concluded:
            raise ImmutableFinOpsRecordException(investigation_id)
        inv.findings.append({"summary": summary, "details": details or {}})
        inv.status = FinOpsInvestigationStatus.FINDINGS_RECORDED
        return inv

    def conclude_investigation(self, tenant_id: str, investigation_id: str) -> FinOpsInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        inv.status = FinOpsInvestigationStatus.CONCLUDED
        inv.is_concluded = True
        inv.concluded_at = datetime.now(timezone.utc)

        # Generate PlatformSnapshot upon conclusion
        snapshot = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="FINOPS_INVESTIGATION",
            resource_id=inv.investigation_id,
            domain_payload=inv.model_dump(mode="json"),
        )
        inv.snapshot_id = snapshot.metadata.snapshot_id
        return inv

    def get_investigation(self, tenant_id: str, investigation_id: str) -> FinOpsInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return inv
