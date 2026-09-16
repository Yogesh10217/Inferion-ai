"""Model Investigation Lifecycle (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory

logger = logging.getLogger(__name__)


class InvestigationStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FINDINGS_RECORDED = "FINDINGS_RECORDED"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    CONCLUDED = "CONCLUDED"


class ModelFinding(BaseModel):
    finding_id: str
    category: str
    summary: str
    severity: str = "HIGH"
    root_cause: str = "Unknown"


class ModelInvestigationEvidence(BaseModel):
    evidence_id: str
    fingerprint: str
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelInvestigation(BaseModel):
    investigation_id: str
    incident_id: str
    model_id: str
    tenant_id: str
    status: InvestigationStatus = InvestigationStatus.OPEN
    findings: List[ModelFinding] = Field(default_factory=list)
    evidence: List[ModelInvestigationEvidence] = Field(default_factory=list)
    snapshot: Optional[PlatformSnapshot] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class ModelInvestigationManager:
    """Manages model investigation lifecycle and generates PlatformSnapshot upon conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, ModelInvestigation] = {}

    def start_investigation(
        self,
        incident_id: str,
        model_id: str,
        tenant_id: str,
    ) -> ModelInvestigation:
        inv_id = f"minv-{uuid.uuid4().hex[:8]}"
        inv = ModelInvestigation(
            investigation_id=inv_id,
            incident_id=incident_id,
            model_id=model_id,
            tenant_id=tenant_id,
            status=InvestigationStatus.OPEN,
        )
        self._investigations[inv_id] = inv
        logger.info(f"[MODEL INVESTIGATION] Started investigation {inv_id} for incident {incident_id} (Tenant: {tenant_id})")
        return inv

    def add_finding(
        self,
        investigation_id: str,
        tenant_id: str,
        category: str,
        summary: str,
        root_cause: str,
    ) -> ModelFinding:
        inv = self.get_investigation(investigation_id, tenant_id)
        finding = ModelFinding(
            finding_id=f"mfind-{uuid.uuid4().hex[:6]}",
            category=category,
            summary=summary,
            root_cause=root_cause,
        )
        inv.findings.append(finding)
        inv.status = InvestigationStatus.FINDINGS_RECORDED
        return finding

    def conclude_investigation(
        self,
        investigation_id: str,
        tenant_id: str,
    ) -> ModelInvestigation:
        inv = self.get_investigation(investigation_id, tenant_id)
        inv.status = InvestigationStatus.CONCLUDED
        inv.concluded_at = datetime.now(timezone.utc)

        snapshot_data = {
            "investigation_id": inv.investigation_id,
            "incident_id": inv.incident_id,
            "model_id": inv.model_id,
            "findings_count": len(inv.findings),
            "concluded_at": inv.concluded_at.isoformat(),
        }

        inv.snapshot = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="MODEL_INVESTIGATION",
            resource_id=inv.investigation_id,
            domain_payload=snapshot_data,
        )

        logger.info(f"[MODEL INVESTIGATION] Concluded investigation {investigation_id} and generated snapshot {inv.snapshot.metadata.snapshot_id}")
        return inv

    def get_investigation(self, investigation_id: str, tenant_id: str) -> ModelInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv:
            raise ValueError(f"Investigation '{investigation_id}' not found.")
        if inv.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return inv
