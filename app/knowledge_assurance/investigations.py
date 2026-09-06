"""Knowledge Assurance Investigations Module.

Provides root-cause analysis, finding generation, evidence collection,
and snapshot generation upon investigation completion.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeInvestigationNotFoundException,
)
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory
from app.platform_contracts.redaction import SensitiveDataSanitizer


class InvestigationStatus(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    EVIDENCE_COLLECTED = "EVIDENCE_COLLECTED"
    FINDINGS_GENERATED = "FINDINGS_GENERATED"
    CONCLUDED = "CONCLUDED"
    ARCHIVED = "ARCHIVED"


class KnowledgeFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"fnd-{uuid.uuid4().hex[:8]}")
    title: str
    description: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    category: str = "TRUST_DEFICIT"  # TRUST_DEFICIT, CONFLICT, STALE_KNOWLEDGE, COVERAGE_GAP
    evidence_refs: List[str] = Field(default_factory=list)
    impact_score: float = 0.5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"evd-{uuid.uuid4().hex[:8]}")
    evidence_type: str
    description: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    checksum: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.checksum:
            raw = f"{self.evidence_id}:{self.evidence_type}:{self.collected_at.isoformat()}"
            self.checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()


class KnowledgeInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"inv-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    target_resource_id: str
    resource_type: str
    reason: str
    status: InvestigationStatus = InvestigationStatus.INITIATED
    findings: List[KnowledgeFinding] = Field(default_factory=list)
    evidence: List[InvestigationEvidence] = Field(default_factory=list)
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concluded_at: Optional[datetime] = None


class KnowledgeInvestigationManager:
    """Manages knowledge assurance investigations."""

    def __init__(self) -> None:
        self._investigations: Dict[str, KnowledgeInvestigation] = {}

    def initiate_investigation(
        self,
        tenant_id: str,
        target_resource_id: str,
        resource_type: str,
        reason: str,
    ) -> KnowledgeInvestigation:
        sanitized_reason = SensitiveDataSanitizer.sanitize(reason)
        inv = KnowledgeInvestigation(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            resource_type=resource_type,
            reason=str(sanitized_reason),
        )
        self._investigations[inv.investigation_id] = inv
        return inv

    def add_evidence(
        self,
        tenant_id: str,
        investigation_id: str,
        evidence_type: str,
        description: str,
        payload: Dict[str, Any],
    ) -> InvestigationEvidence:
        inv = self.get_investigation(tenant_id, investigation_id)
        sanitized_payload = SensitiveDataSanitizer.sanitize(payload)
        evd = InvestigationEvidence(
            evidence_type=evidence_type,
            description=description,
            payload=sanitized_payload if isinstance(sanitized_payload, dict) else {},
        )
        inv.evidence.append(evd)
        inv.status = InvestigationStatus.EVIDENCE_COLLECTED
        inv.updated_at = datetime.now(timezone.utc)
        return evd

    def add_finding(
        self,
        tenant_id: str,
        investigation_id: str,
        title: str,
        description: str,
        severity: str = "MEDIUM",
        category: str = "TRUST_DEFICIT",
        evidence_refs: Optional[List[str]] = None,
        impact_score: float = 0.5,
    ) -> KnowledgeFinding:
        inv = self.get_investigation(tenant_id, investigation_id)
        finding = KnowledgeFinding(
            title=title,
            description=description,
            severity=severity,
            category=category,
            evidence_refs=evidence_refs or [],
            impact_score=impact_score,
        )
        inv.findings.append(finding)
        inv.status = InvestigationStatus.FINDINGS_GENERATED
        inv.updated_at = datetime.now(timezone.utc)
        return finding

    def conclude_investigation(
        self, tenant_id: str, investigation_id: str
    ) -> KnowledgeInvestigation:
        inv = self.get_investigation(tenant_id, investigation_id)
        inv.status = InvestigationStatus.CONCLUDED
        now = datetime.now(timezone.utc)
        inv.concluded_at = now
        inv.updated_at = now

        # Generate snapshot on conclusion using SnapshotFactory
        snapshot: PlatformSnapshot = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="KNOWLEDGE_INVESTIGATION",
            resource_id=inv.investigation_id,
            domain_payload={
                "investigation_id": inv.investigation_id,
                "target_resource_id": inv.target_resource_id,
                "findings_count": len(inv.findings),
                "evidence_count": len(inv.evidence),
                "concluded_at": now.isoformat(),
            },
        )
        inv.snapshot_id = snapshot.snapshot_id
        return inv

    def get_investigation(self, tenant_id: str, investigation_id: str) -> KnowledgeInvestigation:
        if investigation_id not in self._investigations:
            raise KnowledgeInvestigationNotFoundException()
        inv = self._investigations[investigation_id]
        if inv.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return inv

    def list_investigations(
        self, tenant_id: str, target_resource_id: Optional[str] = None
    ) -> List[KnowledgeInvestigation]:
        results = [
            inv for inv in self._investigations.values() if inv.tenant_id == tenant_id
        ]
        if target_resource_id:
            results = [inv for inv in results if inv.target_resource_id == target_resource_id]
        return results
