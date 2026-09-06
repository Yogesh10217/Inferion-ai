"""Immutable Identity Evidence Subsystem."""

from datetime import datetime, timezone
import hashlib
import json
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import (
    CrossTenantIdentityAssuranceException,
    ImmutableIdentityRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class IdentityEvidenceIntegrity(BaseModel):
    checksum: str
    algorithm: str = "SHA-256"
    verified: bool = True


class IdentityEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str
    source: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    evidence_items: List[IdentityEvidence] = Field(default_factory=list)
    integrity: Optional[IdentityEvidenceIntegrity] = None
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityEvidenceManager:
    """Manages immutable, tenant-isolated identity evidence bundles with SHA-256 integrity."""

    def __init__(self, sanitizer: Optional[SensitiveDataSanitizer] = None) -> None:
        self.sanitizer = sanitizer or SensitiveDataSanitizer()
        self._bundles: Dict[str, IdentityEvidenceBundle] = {}

    def create_evidence_bundle(
        self,
        tenant_id: str,
        identity_id: str,
        evidence_items: List[IdentityEvidence],
    ) -> IdentityEvidenceBundle:
        sanitized_items = []
        for item in evidence_items:
            sanitized_payload = self.sanitizer.sanitize(item.payload)
            sanitized_items.append(
                IdentityEvidence(
                    evidence_id=item.evidence_id,
                    evidence_type=item.evidence_type,
                    source=item.source,
                    payload=sanitized_payload,
                    collected_at=item.collected_at,
                )
            )

        bundle = IdentityEvidenceBundle(
            tenant_id=tenant_id,
            identity_id=identity_id,
            evidence_items=sanitized_items,
        )
        self.finalize_bundle(bundle)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def finalize_bundle(self, bundle: IdentityEvidenceBundle) -> IdentityEvidenceBundle:
        if bundle.is_finalized:
            raise ImmutableIdentityRecordException("Evidence bundle is already finalized and immutable.")

        raw_data = json.dumps(
            {
                "tenant_id": bundle.tenant_id,
                "identity_id": bundle.identity_id,
                "items": [item.model_dump(mode="json") for item in bundle.evidence_items],
            },
            sort_keys=True,
        ).encode("utf-8")

        checksum = hashlib.sha256(raw_data).hexdigest()
        bundle.integrity = IdentityEvidenceIntegrity(checksum=checksum)
        bundle.is_finalized = True
        return bundle

    def verify_integrity(self, tenant_id: str, bundle_id: str) -> bool:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if not bundle.integrity:
            return False

        raw_data = json.dumps(
            {
                "tenant_id": bundle.tenant_id,
                "identity_id": bundle.identity_id,
                "items": [item.model_dump(mode="json") for item in bundle.evidence_items],
            },
            sort_keys=True,
        ).encode("utf-8")

        checksum = hashlib.sha256(raw_data).hexdigest()
        return checksum == bundle.integrity.checksum

    def get_bundle(self, tenant_id: str, bundle_id: str) -> IdentityEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle or bundle.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return bundle
