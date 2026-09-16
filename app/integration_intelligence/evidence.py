"""Integration Evidence Management (Phase 5.40)."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    ImmutableIntegrationRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class IntegrationEvidenceIntegrity(BaseModel):
    sha256_hash: str
    verified: bool = True
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_int_{uuid.uuid4().hex[:8]}")
    evidence_type: str  # EXECUTION_RECORD, VERIFICATION_CHECK, RECOVERY_ACTION
    reference_id: str
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"ev_bundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    items: List[IntegrationEvidence] = Field(default_factory=list)
    integrity: Optional[IntegrationEvidenceIntegrity] = None
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None


class IntegrationEvidenceManager:
    """Manages sanitized integration evidence collection with SHA-256 integrity."""

    def __init__(self) -> None:
        self._bundles: Dict[str, IntegrationEvidenceBundle] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def create_bundle(self, tenant_id: str, title: str) -> IntegrationEvidenceBundle:
        bundle = IntegrationEvidenceBundle(tenant_id=tenant_id, title=title)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_evidence(
        self,
        tenant_id: str,
        bundle_id: str,
        evidence_type: str,
        reference_id: str,
        payload: Dict[str, Any],
    ) -> IntegrationEvidence:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableIntegrationRecordException(bundle_id)

        sanitized = self.sanitizer.sanitize(payload)
        evidence = IntegrationEvidence(
            evidence_type=evidence_type,
            reference_id=reference_id,
            sanitized_payload=sanitized,
        )
        bundle.items.append(evidence)
        return evidence

    def finalize_bundle(self, tenant_id: str, bundle_id: str) -> IntegrationEvidenceBundle:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableIntegrationRecordException(bundle_id)

        raw_str = json.dumps(
            [item.model_dump(mode="json") for item in bundle.items],
            sort_keys=True,
        )
        sha256_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        bundle.integrity = IntegrationEvidenceIntegrity(sha256_hash=sha256_hash, verified=True)
        bundle.is_finalized = True
        bundle.finalized_at = datetime.now(timezone.utc)
        return bundle

    def get_bundle(self, tenant_id: str, bundle_id: str) -> IntegrationEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle or bundle.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return bundle
