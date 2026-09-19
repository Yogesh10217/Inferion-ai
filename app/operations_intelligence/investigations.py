"""Operational Investigation Lifecycle & Snapshot Generation (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    ImmutableOperationsRecordException,
    InvalidAccessStateTransitionException,
)
from app.platform_contracts.snapshots import SnapshotFactory


class InvestigationStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FINDINGS_RECORDED = "FINDINGS_RECORDED"
    ROOT_CAUSE_ANALYZED = "ROOT_CAUSE_ANALYZED"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    CONCLUDED = "CONCLUDED"


class InvestigationFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:8]}")
    title: str
    severity: str = "HIGH"
    details: Dict[str, Any] = Field(default_factory=dict)


class OperationalInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"inv_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    target_incident_id: str
    status: InvestigationStatus = InvestigationStatus.OPEN
    findings: List[InvestigationFinding] = Field(default_factory=list)
    root_cause_analysis_id: Optional[str] = None
    is_concluded: bool = False
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class OperationalInvestigationManager:
    """Manages operational investigation lifecycle and snapshot generation upon conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, OperationalInvestigation] = {}

    def open_investigation(self, tenant_id: str, title: str, target_incident_id: str) -> OperationalInvestigation:
        inv = OperationalInvestigation(
            tenant_id=tenant_id,
            title=title,
            target_incident_id=target_incident_id,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def start_investigating(self, tenant_id: str, investigation_id: str) -> OperationalInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.status != InvestigationStatus.OPEN:
            raise InvalidAccessStateTransitionException(inv.status.value, InvestigationStatus.INVESTIGATING.value)
        inv.status = InvestigationStatus.INVESTIGATING
        return inv

    def record_finding(
        self,
        tenant_id: str,
        investigation_id: str,
        title: str,
        severity: str = "HIGH",
        details: Optional[Dict[str, Any]] = None,
    ) -> OperationalInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.is_concluded:
            raise ImmutableOperationsRecordException(investigation_id)
        finding = InvestigationFinding(title=title, severity=severity, details=details or {})
        inv.findings.append(finding)
        inv.status = InvestigationStatus.FINDINGS_RECORDED
        return inv

    def set_root_cause_analyzed(
        self, tenant_id: str, investigation_id: str, root_cause_analysis_id: str
    ) -> OperationalInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.is_concluded:
            raise ImmutableOperationsRecordException(investigation_id)
        inv.root_cause_analysis_id = root_cause_analysis_id
        inv.status = InvestigationStatus.ROOT_CAUSE_ANALYZED
        return inv

    def conclude_investigation(self, tenant_id: str, investigation_id: str) -> OperationalInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.status not in [
            InvestigationStatus.FINDINGS_RECORDED,
            InvestigationStatus.ROOT_CAUSE_ANALYZED,
            InvestigationStatus.REMEDIATION_PLANNED,
        ]:
            raise InvalidAccessStateTransitionException(inv.status.value, InvestigationStatus.CONCLUDED.value)
        inv.status = InvestigationStatus.CONCLUDED
        inv.is_concluded = True
        inv.concluded_at = datetime.now(timezone.utc)

        # Generate PlatformSnapshot for concluded investigation
        snapshot = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="OPERATIONAL_INVESTIGATION",
            resource_id=inv.investigation_id,
            domain_payload=inv.model_dump(mode="json"),
        )
        inv.snapshot_id = snapshot.metadata.snapshot_id
        return inv

    def get_investigation(self, tenant_id: str, investigation_id: str) -> OperationalInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return inv
