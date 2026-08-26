"""Knowledge Investigation Management Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeInvestigationStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CONCLUDED = "CONCLUDED"
    DISMISSED = "DISMISSED"


class KnowledgeFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"kfind_{uuid.uuid4().hex[:8]}")
    title: str
    description: str
    severity: str = "MEDIUM"


class KnowledgeInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"kinv_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    status: KnowledgeInvestigationStatus = KnowledgeInvestigationStatus.OPEN
    findings: List[KnowledgeFinding] = Field(default_factory=list)
    summary: str = ""
    snapshot: Optional[PlatformSnapshot] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class KnowledgeInvestigationManager:
    """Manages knowledge investigations and generates immutable PlatformSnapshots upon conclusion."""

    def __init__(self) -> None:
        self._investigations: Dict[str, KnowledgeInvestigation] = {}

    def initiate_investigation(
        self,
        tenant_id: str,
        target_id: str,
        initial_finding_title: str = "Knowledge Discrepancy",
        initial_finding_desc: str = "Investigating conflict or staleness",
    ) -> KnowledgeInvestigation:
        finding = KnowledgeFinding(title=initial_finding_title, description=initial_finding_desc)
        inv = KnowledgeInvestigation(
            tenant_id=tenant_id,
            target_id=target_id,
            findings=[finding],
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def conclude_investigation(
        self,
        investigation_id: str,
        tenant_id: str,
        summary: str,
    ) -> KnowledgeInvestigation:
        inv = self._investigations.get(investigation_id)
        if not inv or inv.tenant_id != tenant_id:
            raise KeyError("Investigation not found or tenant mismatch")

        inv.status = KnowledgeInvestigationStatus.CONCLUDED
        inv.summary = summary
        inv.concluded_at = datetime.now(timezone.utc)

        snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="KNOWLEDGE_INVESTIGATION",
            resource_id=investigation_id,
            domain_payload=inv.model_dump(),
        )
        inv.snapshot = snap
        return inv
