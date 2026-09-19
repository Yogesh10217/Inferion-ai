"""Resilience Evidence Bundles Subsystem (Phase 5.37)."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import ImmutableResilienceRecordException


class ResilienceEvidenceIntegrity(BaseModel):
    checksum_sha256: str
    is_verified: bool = True


class ResilienceEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"resev_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    evidence_type: str
    content: Dict[str, Any] = Field(default_factory=dict)
    sanitized_content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"resevbundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    recovery_plan_id: str
    evidences: List[ResilienceEvidence] = Field(default_factory=list)
    checksum_sha256: str = ""
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceEvidenceManager:
    """Resilience Evidence Bundle Manager with SHA-256 integrity and secret sanitization."""

    def __init__(
        self,
        sanitizer: Optional[SensitiveDataSanitizer] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.sanitizer = sanitizer or SensitiveDataSanitizer()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._bundles: Dict[str, ResilienceEvidenceBundle] = {}

    def create_bundle(self, tenant_id: str, recovery_plan_id: str) -> ResilienceEvidenceBundle:
        bundle = ResilienceEvidenceBundle(tenant_id=tenant_id, recovery_plan_id=recovery_plan_id)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_evidence(
        self, bundle_id: str, tenant_id: str, evidence_type: str, raw_content: Dict[str, Any]
    ) -> ResilienceEvidence:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            bundle = self.create_bundle(tenant_id, "default_plan")

        if bundle.is_finalized:
            raise ImmutableResilienceRecordException(f"Evidence bundle '{bundle_id}' is finalized and immutable.")

        sanitized = self.sanitizer.sanitize_copy(raw_content)
        ev = ResilienceEvidence(
            tenant_id=tenant_id,
            evidence_type=evidence_type,
            content=raw_content,
            sanitized_content=sanitized,
        )
        bundle.evidences.append(ev)
        return ev

    def finalize_bundle(self, bundle_id: str, tenant_id: str) -> ResilienceEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            raise ImmutableResilienceRecordException(f"Bundle '{bundle_id}' not found.")

        if bundle.is_finalized:
            return bundle

        # Calculate deterministic SHA-256
        data_str = json.dumps([e.sanitized_content for e in bundle.evidences], sort_keys=True, default=str)
        bundle.checksum_sha256 = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        bundle.is_finalized = True
        return bundle
