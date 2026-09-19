"""Immutable decision evidence bundle management with SHA-256 integrity."""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    DecisionEvidenceNotFoundException,
    ImmutableDecisionRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class DecisionEvidenceReference(BaseModel):
    reference_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_domain: str
    resource_type: str
    resource_id: str
    summary: str = ""
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    decision_id: str
    evidence_type: str
    title: str
    description: str = ""
    references: List[DecisionEvidenceReference] = Field(default_factory=list)
    fingerprint: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def calculate_fingerprint(self) -> str:
        payload = (
            f"{self.evidence_id}:{self.tenant_id}:{self.decision_id}:{self.evidence_type}:{self.created_at.isoformat()}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DecisionEvidenceIntegrity(BaseModel):
    is_valid: bool
    calculated_fingerprint: str
    stored_fingerprint: str
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    items: List[DecisionEvidence] = Field(default_factory=list)
    bundle_fingerprint: Optional[str] = None
    is_immutable: bool = False
    finalized_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_bundle_fingerprint(self) -> str:
        item_fps = "-".join([item.fingerprint or item.calculate_fingerprint() for item in self.items])
        payload = f"{self.bundle_id}:{self.decision_id}:{self.tenant_id}:{item_fps}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DecisionEvidenceManager:
    """Manages immutable evidence bundles for decisions with zero secret storage."""

    def __init__(self) -> None:
        self._bundles: Dict[str, DecisionEvidenceBundle] = {}

    def create_evidence_bundle(
        self,
        tenant_id: str,
        decision_id: str,
        evidence_items: Optional[List[DecisionEvidence]] = None,
    ) -> DecisionEvidenceBundle:
        sanitized_items = []
        if evidence_items:
            for item in evidence_items:
                item.metadata = SensitiveDataSanitizer.sanitize_metadata(item.metadata)
                item.fingerprint = item.calculate_fingerprint()
                sanitized_items.append(item)

        bundle = DecisionEvidenceBundle(
            tenant_id=tenant_id,
            decision_id=decision_id,
            items=sanitized_items,
        )
        bundle.bundle_fingerprint = bundle.calculate_bundle_fingerprint()
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def get_bundle(self, bundle_id: str, tenant_id: str) -> DecisionEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            raise DecisionEvidenceNotFoundException(f"Evidence bundle '{bundle_id}' not found")
        if bundle.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return bundle

    def finalize_bundle(self, bundle_id: str, tenant_id: str) -> DecisionEvidenceBundle:
        bundle = self.get_bundle(bundle_id, tenant_id)
        if bundle.is_immutable:
            raise ImmutableDecisionRecordException(f"Bundle '{bundle_id}' is already finalized")
        bundle.is_immutable = True
        bundle.finalized_at = datetime.now(timezone.utc)
        bundle.bundle_fingerprint = bundle.calculate_bundle_fingerprint()
        return bundle

    def verify_integrity(self, bundle_id: str, tenant_id: str) -> DecisionEvidenceIntegrity:
        bundle = self.get_bundle(bundle_id, tenant_id)
        calc_fp = bundle.calculate_bundle_fingerprint()
        is_valid = calc_fp == bundle.bundle_fingerprint
        return DecisionEvidenceIntegrity(
            is_valid=is_valid,
            calculated_fingerprint=calc_fp,
            stored_fingerprint=bundle.bundle_fingerprint or "",
        )
