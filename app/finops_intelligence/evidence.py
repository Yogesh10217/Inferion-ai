"""Financial Evidence Management (Phase 5.42)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
import hashlib
import json
from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import (
    CrossTenantFinOpsIntelligenceException,
    ImmutableFinOpsRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class FinOpsEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_fin_{uuid.uuid4().hex[:8]}")
    evidence_type: str  # COST_LEDGER_ENTRY, USAGE_TELEMETRY, ALLOCATION_PROOF, VERIFICATION_RECORD
    reference_id: str
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"ev_bundle_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    items: List[FinOpsEvidence] = Field(default_factory=list)
    sha256_hash: Optional[str] = None
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsEvidenceManager:
    """Manages financial evidence collection with SHA-256 integrity validation."""

    def __init__(self) -> None:
        self._bundles: Dict[str, FinOpsEvidenceBundle] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def create_bundle(self, tenant_id: str, title: str) -> FinOpsEvidenceBundle:
        bundle = FinOpsEvidenceBundle(tenant_id=tenant_id, title=title)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_evidence(
        self,
        tenant_id: str,
        bundle_id: str,
        evidence_type: str,
        reference_id: str,
        payload: Dict[str, Any],
    ) -> FinOpsEvidence:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableFinOpsRecordException(bundle_id)

        sanitized = self.sanitizer.sanitize(payload)
        item = FinOpsEvidence(
            evidence_type=evidence_type,
            reference_id=reference_id,
            sanitized_payload=sanitized,
        )
        bundle.items.append(item)
        return item

    def finalize_bundle(self, tenant_id: str, bundle_id: str) -> FinOpsEvidenceBundle:
        bundle = self.get_bundle(tenant_id, bundle_id)
        if bundle.is_finalized:
            raise ImmutableFinOpsRecordException(bundle_id)

        raw_str = json.dumps(
            [item.model_dump(mode="json") for item in bundle.items],
            sort_keys=True,
        )
        bundle.sha256_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        bundle.is_finalized = True
        return bundle

    def get_bundle(self, tenant_id: str, bundle_id: str) -> FinOpsEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle or bundle.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return bundle
