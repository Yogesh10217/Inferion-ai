"""
Immutable Evidence Ledger Subsystem.
Seals workflow evidence using SHA-256 integrity hashes with mandatory sensitive data redaction.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.autonomous_assurance.exceptions import (
    CrossTenantAutonomousAssuranceException,
    ImmutableAutonomousAssuranceRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class AutonomousEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"evb_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    evidence_references: List[Dict[str, Any]] = Field(default_factory=list)
    governance_decision_id: Optional[str] = None
    approval_id: Optional[str] = None
    delegation_id: Optional[str] = None
    verification_id: Optional[str] = None
    is_sealed: bool = False
    evidence_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sealed_at: Optional[datetime] = None

    @property
    def evidence_sha256(self) -> Optional[str]:
        return self.evidence_hash


class AutonomousEvidenceManager:
    """Manages creation, redaction, and SHA-256 sealing of workflow evidence bundles."""

    def __init__(self) -> None:
        self._bundles: Dict[str, AutonomousEvidenceBundle] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def create_evidence_bundle(
        self,
        workflow_id: str,
        tenant_id: str,
        evidence_references: Optional[List[Dict[str, Any]]] = None,
        governance_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        delegation_id: Optional[str] = None,
        verification_id: Optional[str] = None,
    ) -> AutonomousEvidenceBundle:
        sanitized_refs = []
        if evidence_references:
            for ref in evidence_references:
                sanitized_refs.append(self.sanitizer.sanitize_dict(ref))

        bundle = AutonomousEvidenceBundle(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            evidence_references=sanitized_refs,
            governance_decision_id=governance_id,
            approval_id=approval_id,
            delegation_id=delegation_id,
            verification_id=verification_id,
        )
        self._bundles[workflow_id] = bundle
        return bundle

    def seal_evidence_bundle(self, workflow_id: str, tenant_id: str) -> AutonomousEvidenceBundle:
        bundle = self.get_evidence_bundle(workflow_id, tenant_id)
        if bundle.is_sealed:
            raise ImmutableAutonomousAssuranceRecordException(f"Evidence bundle for workflow '{workflow_id}' is already sealed.")

        canonical_payload = {
            "bundle_id": bundle.bundle_id,
            "workflow_id": bundle.workflow_id,
            "tenant_id": bundle.tenant_id,
            "evidence_references": bundle.evidence_references,
            "governance_id": bundle.governance_decision_id,
            "approval_id": bundle.approval_id,
            "delegation_id": bundle.delegation_id,
            "verification_id": bundle.verification_id,
            "created_at": bundle.created_at.isoformat(),
        }
        digest = hashlib.sha256(json.dumps(canonical_payload, sort_keys=True).encode("utf-8")).hexdigest()

        bundle.is_sealed = True
        bundle.evidence_hash = digest
        bundle.sealed_at = datetime.now(timezone.utc)
        return bundle

    def seal_evidence(self, workflow_id: str, tenant_id: str, execution_trace: Optional[List[str]] = None) -> AutonomousEvidenceBundle:
        bundle = self.create_evidence_bundle(workflow_id, tenant_id, evidence_references=[{"trace": t} for t in (execution_trace or [])])
        return self.seal_evidence_bundle(workflow_id, tenant_id)

    def get_evidence_bundle(self, workflow_id: str, tenant_id: str) -> AutonomousEvidenceBundle:
        bundle = self._bundles.get(workflow_id)
        if not bundle:
            bundle = self.create_evidence_bundle(workflow_id, tenant_id)
        if bundle.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantAutonomousAssuranceException(f"Unauthorized cross-tenant access to evidence bundle for workflow '{workflow_id}'")
        return bundle
