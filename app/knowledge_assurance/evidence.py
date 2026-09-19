"""Knowledge Assurance Evidence Module.

Provides tamper-evident, SHA-256 fingerprint verified immutable evidence bundles.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    ImmutableKnowledgeRecordException,
    KnowledgeEvidenceNotFoundException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeEvidenceIntegrity(BaseModel):
    checksum_sha256: str
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_valid: bool = True


class KnowledgeEvidenceReference(BaseModel):
    ref_id: str
    resource_type: str
    description: str


class KnowledgeEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ke-evd-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    evidence_type: str
    title: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    references: List[KnowledgeEvidenceReference] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"ke-bndl-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    title: str
    evidences: List[KnowledgeEvidence] = Field(default_factory=list)
    is_finalized: bool = False
    sha256_fingerprint: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None

    def compute_fingerprint(self) -> str:
        serialized = {
            "bundle_id": self.bundle_id,
            "tenant_id": self.tenant_id,
            "title": self.title,
            "evidences": [e.model_dump(mode="json") for e in self.evidences],
        }
        raw_bytes = json.dumps(serialized, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()


class KnowledgeEvidenceManager:
    """Manages immutable evidence collection and integrity verification."""

    def __init__(self) -> None:
        self._bundles: Dict[str, KnowledgeEvidenceBundle] = {}

    def create_bundle(self, tenant_id: str, title: str) -> KnowledgeEvidenceBundle:
        bundle = KnowledgeEvidenceBundle(tenant_id=tenant_id, title=title)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_evidence(
        self,
        tenant_id: str,
        bundle_id: str,
        evidence_type: str,
        title: str,
        payload: Dict[str, Any],
        references: Optional[List[KnowledgeEvidenceReference]] = None,
    ) -> KnowledgeEvidence:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableKnowledgeRecordException(f"Bundle {bundle_id} is finalized and immutable.")

        sanitized_payload = SensitiveDataSanitizer.sanitize(payload)
        evd = KnowledgeEvidence(
            tenant_id=tenant_id,
            evidence_type=evidence_type,
            title=title,
            payload=sanitized_payload if isinstance(sanitized_payload, dict) else {},
            references=references or [],
        )
        bundle.evidences.append(evd)
        return evd

    def finalize_bundle(self, tenant_id: str, bundle_id: str) -> KnowledgeEvidenceBundle:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableKnowledgeRecordException(f"Bundle {bundle_id} is already finalized.")

        bundle.sha256_fingerprint = bundle.compute_fingerprint()
        bundle.is_finalized = True
        bundle.finalized_at = datetime.now(timezone.utc)
        return bundle

    def verify_bundle_integrity(self, tenant_id: str, bundle_id: str) -> KnowledgeEvidenceIntegrity:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if not bundle.is_finalized:
            return KnowledgeEvidenceIntegrity(
                checksum_sha256="",
                is_valid=False,
            )

        computed = bundle.compute_fingerprint()
        is_valid = computed == bundle.sha256_fingerprint
        return KnowledgeEvidenceIntegrity(
            checksum_sha256=computed,
            is_valid=is_valid,
        )

    def get_bundle(self, tenant_id: str, bundle_id: str) -> KnowledgeEvidenceBundle:
        if bundle_id not in self._bundles:
            raise KnowledgeEvidenceNotFoundException(f"Evidence bundle {bundle_id} not found.")
        bundle = self._bundles[bundle_id]
        if bundle.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return bundle

    def list_bundles(self, tenant_id: str) -> List[KnowledgeEvidenceBundle]:
        return [b for b in self._bundles.values() if b.tenant_id == tenant_id]
