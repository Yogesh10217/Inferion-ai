"""Operational Evidence Management (Phase 5.41)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
import hashlib
import json
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    ImmutableOperationsRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class OperationalEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_op_{uuid.uuid4().hex[:8]}")
    evidence_type: str  # ALERT_LOG, INCIDENT_TRACE, REMEDIATION_RECORD, VERIFICATION_RESULT
    reference_id: str
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"ev_bundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    items: List[OperationalEvidence] = Field(default_factory=list)
    sha256_hash: Optional[str] = None
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalEvidenceManager:
    """Manages operational evidence collection with SHA-256 integrity."""

    def __init__(self) -> None:
        self._bundles: Dict[str, OperationalEvidenceBundle] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def create_bundle(self, tenant_id: str, title: str) -> OperationalEvidenceBundle:
        bundle = OperationalEvidenceBundle(tenant_id=tenant_id, title=title)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_evidence(
        self,
        tenant_id: str,
        bundle_id: str,
        evidence_type: str,
        reference_id: str,
        payload: Dict[str, Any],
    ) -> OperationalEvidence:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableOperationsRecordException(bundle_id)

        sanitized = self.sanitizer.sanitize(payload)
        item = OperationalEvidence(
            evidence_type=evidence_type,
            reference_id=reference_id,
            sanitized_payload=sanitized,
        )
        bundle.items.append(item)
        return item

    def finalize_bundle(self, tenant_id: str, bundle_id: str) -> OperationalEvidenceBundle:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableOperationsRecordException(bundle_id)

        raw_str = json.dumps(
            [item.model_dump(mode="json") for item in bundle.items],
            sort_keys=True,
        )
        bundle.sha256_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        bundle.is_finalized = True
        return bundle

    def get_bundle(self, tenant_id: str, bundle_id: str) -> OperationalEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle or bundle.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return bundle
