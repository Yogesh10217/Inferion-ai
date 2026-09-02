"""Access Investigation Lifecycle (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import (
    CrossTenantAccessIntelligenceException,
    InvalidAccessStateTransitionException,
    ImmutableAccessRecordException,
)
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory


class AccessInvestigationStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FINDINGS_RECORDED = "FINDINGS_RECORDED"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    CONCLUDED = "CONCLUDED"


class AccessFinding(BaseModel):
    """Specific finding recorded during investigation."""
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:8]}")
    title: str
    severity: str = "HIGH"
    details: Dict[str, Any] = Field(default_factory=dict)


class AccessInvestigation(BaseModel):
    """Access Investigation Lifecycle Representation."""
    investigation_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    target_identity_id: str
    status: AccessInvestigationStatus = AccessInvestigationStatus.OPEN
    findings: List[AccessFinding] = Field(default_factory=list)
    remediation_plan_id: Optional[str] = None
    is_concluded: bool = False
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessInvestigationManager:
    """Manages access investigation lifecycle and snapshot generation."""

    def __init__(self) -> None:
        self._investigations: Dict[str, AccessInvestigation] = {}

    def open_investigation(
        self,
        tenant_id: str,
        title: str,
        target_identity_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessInvestigation:
        inv = AccessInvestigation(
            tenant_id=tenant_id,
            title=title,
            target_identity_id=target_identity_id,
            metadata=metadata or {},
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def start_investigating(self, tenant_id: str, investigation_id: str) -> AccessInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.status != AccessInvestigationStatus.OPEN:
            raise InvalidAccessStateTransitionException(inv.status.value, AccessInvestigationStatus.INVESTIGATING.value)
        inv.status = AccessInvestigationStatus.INVESTIGATING
        return inv

    def record_finding(self, tenant_id: str, investigation_id: str, title: str, severity: str = "HIGH", details: Optional[Dict[str, Any]] = None) -> AccessInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.is_concluded:
            raise ImmutableAccessRecordException(investigation_id)
        finding = AccessFinding(title=title, severity=severity, details=details or {})
        inv.findings.append(finding)
        inv.status = AccessInvestigationStatus.FINDINGS_RECORDED
        return inv

    def set_remediation_planned(self, tenant_id: str, investigation_id: str, remediation_plan_id: str) -> AccessInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.is_concluded:
            raise ImmutableAccessRecordException(investigation_id)
        inv.remediation_plan_id = remediation_plan_id
        inv.status = AccessInvestigationStatus.REMEDIATION_PLANNED
        return inv

    def conclude_investigation(self, tenant_id: str, investigation_id: str) -> AccessInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        if inv.status not in [AccessInvestigationStatus.FINDINGS_RECORDED, AccessInvestigationStatus.REMEDIATION_PLANNED]:
            raise InvalidAccessStateTransitionException(inv.status.value, AccessInvestigationStatus.CONCLUDED.value)
        inv.status = AccessInvestigationStatus.CONCLUDED
        inv.is_concluded = True
        inv.concluded_at = datetime.now(timezone.utc)

        # Generate PlatformSnapshot for finalized investigation
        snapshot = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="ACCESS_INVESTIGATION",
            resource_id=inv.investigation_id,
            domain_payload=inv.model_dump(mode="json"),
        )
        inv.snapshot_id = snapshot.metadata.snapshot_id
        return inv

    def get_investigation(self, tenant_id: str, investigation_id: str) -> AccessInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return inv

    def list_investigations(self, tenant_id: str, status: Optional[AccessInvestigationStatus] = None) -> List[AccessInvestigation]:
        results = [i for i in self._investigations.values() if i.tenant_id == tenant_id]
        if status:
            results = [i for i in results if i.status == status]
        return results
