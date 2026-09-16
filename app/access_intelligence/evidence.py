"""Access Evidence Management (Phase 5.39)."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import (
    AccessEvidenceIntegrityException,
    CrossTenantAccessIntelligenceException,
    ImmutableAccessRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class AccessEvidenceIntegrity(BaseModel):
    """Integrity calculation metadata."""
    sha256_hash: str
    verified: bool = True
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessEvidence(BaseModel):
    """Single item of access evidence."""
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:8]}")
    evidence_type: str  # AUTHORIZATION_RECORD, CERTIFICATION_DECISION, REVIEW_DECISION, AUDIT_SIGNAL
    reference_id: str
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessEvidenceBundle(BaseModel):
    """Immutable Access Evidence Bundle."""
    bundle_id: str = Field(default_factory=lambda: f"ev_bundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    items: List[AccessEvidence] = Field(default_factory=list)
    integrity: Optional[AccessEvidenceIntegrity] = None
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None


class AccessEvidenceManager:
    """Manages access evidence collection, sanitization, and SHA-256 integrity."""

    def __init__(self) -> None:
        self._bundles: Dict[str, AccessEvidenceBundle] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def create_bundle(self, tenant_id: str, title: str) -> AccessEvidenceBundle:
        bundle = AccessEvidenceBundle(tenant_id=tenant_id, title=title)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_evidence(
        self,
        tenant_id: str,
        bundle_id: str,
        evidence_type: str,
        reference_id: str,
        payload: Dict[str, Any],
    ) -> AccessEvidence:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableAccessRecordException(bundle_id)

        sanitized = self.sanitizer.sanitize(payload)
        evidence = AccessEvidence(
            evidence_type=evidence_type,
            reference_id=reference_id,
            sanitized_payload=sanitized,
        )
        bundle.items.append(evidence)
        return evidence

    def finalize_bundle(self, tenant_id: str, bundle_id: str) -> AccessEvidenceBundle:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableAccessRecordException(bundle_id)

        raw_str = json.dumps(
            [item.model_dump(mode="json") for item in bundle.items],
            sort_keys=True,
        )
        sha256_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        bundle.integrity = AccessEvidenceIntegrity(sha256_hash=sha256_hash, verified=True)
        bundle.is_finalized = True
        bundle.finalized_at = datetime.now(timezone.utc)
        return bundle

    def verify_bundle_integrity(self, tenant_id: str, bundle_id: str) -> bool:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if not bundle.integrity or not bundle.is_finalized:
            return False

        raw_str = json.dumps(
            [item.model_dump(mode="json") for item in bundle.items],
            sort_keys=True,
        )
        computed_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        if computed_hash != bundle.integrity.sha256_hash:
            raise AccessEvidenceIntegrityException(bundle_id, "SHA-256 mismatch.")
        return True

    def get_bundle(self, tenant_id: str, bundle_id: str) -> AccessEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle or bundle.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return bundle
