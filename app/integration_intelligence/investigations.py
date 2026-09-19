"""Integration Investigation Lifecycle (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    ImmutableIntegrationRecordException,
    InvalidAccessStateTransitionException,
)
from app.platform_contracts.snapshots import SnapshotFactory


class InvestigationStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FINDINGS_RECORDED = "FINDINGS_RECORDED"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    CONCLUDED = "CONCLUDED"


class IntegrationFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:8]}")
    title: str
    severity: str = "HIGH"
    details: Dict[str, Any] = Field(default_factory=dict)


class IntegrationInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"inv_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    target_workflow_id: str
    status: InvestigationStatus = InvestigationStatus.OPEN
    findings: List[IntegrationFinding] = Field(default_factory=list)
    remediation_plan_id: Optional[str] = None
    is_concluded: bool = False
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class IntegrationInvestigationManager:
    """Manages integration investigation lifecycle and PlatformSnapshot generation upon conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, IntegrationInvestigation] = {}

    def open_investigation(self, tenant_id: str, title: str, target_workflow_id: str) -> IntegrationInvestigation:
        inv = IntegrationInvestigation(
            tenant_id=tenant_id,
            title=title,
            target_workflow_id=target_workflow_id,
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def start_investigating(self, tenant_id: str, investigation_id: str) -> IntegrationInvestigation:
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
    ) -> IntegrationInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.is_concluded:
            raise ImmutableIntegrationRecordException(investigation_id)
        finding = IntegrationFinding(title=title, severity=severity, details=details or {})
        inv.findings.append(finding)
        inv.status = InvestigationStatus.FINDINGS_RECORDED
        return inv

    def conclude_investigation(self, tenant_id: str, investigation_id: str) -> IntegrationInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.status not in [InvestigationStatus.FINDINGS_RECORDED, InvestigationStatus.REMEDIATION_PLANNED]:
            raise InvalidAccessStateTransitionException(inv.status.value, InvestigationStatus.CONCLUDED.value)
        inv.status = InvestigationStatus.CONCLUDED
        inv.is_concluded = True
        inv.concluded_at = datetime.now(timezone.utc)

        # Generate PlatformSnapshot for concluded investigation
        snapshot = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="INTEGRATION_INVESTIGATION",
            resource_id=inv.investigation_id,
            domain_payload=inv.model_dump(mode="json"),
        )
        inv.snapshot_id = snapshot.metadata.snapshot_id
        return inv

    def get_investigation(self, tenant_id: str, investigation_id: str) -> IntegrationInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return inv
