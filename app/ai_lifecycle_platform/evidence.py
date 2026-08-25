"""Lifecycle Evidence References Subsystem (Phase 5.33)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.ai_lifecycle_platform.exceptions import ImmutableLifecycleRecordException, CrossTenantLifecycleAccessException


class LifecycleEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"levid_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source: str
    content_reference: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sha256_hash: str = ""


class LifecycleEvidenceIntegrity(BaseModel):
    is_valid: bool = True
    sha256_hash: str = ""


class LifecycleEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"levb_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    evidences: List[LifecycleEvidence] = Field(default_factory=list)
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(resource_id=self.bundle_id, tenant_id=self.tenant_id)


class LifecycleEvidenceManager:
    """Manages sanitized, fingerprinted, and immutable lifecycle evidence bundles."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._bundles: Dict[str, LifecycleEvidenceBundle] = {}

    def create_evidence_bundle(
        self,
        tenant_id: str,
        title: str,
        evidences: List[LifecycleEvidence],
    ) -> LifecycleEvidenceBundle:
        sanitized_evidences = []
        for ev in evidences:
            sanitized_meta = self.sanitizer.sanitize_copy(ev.metadata)
            fp = FingerprintGenerator.generate({"source": ev.source, "ref": ev.content_reference, "meta": sanitized_meta})
            sanitized_ev = LifecycleEvidence(
                tenant_id=tenant_id,
                source=ev.source,
                content_reference=ev.content_reference,
                metadata=sanitized_meta,
                sha256_hash=fp,
            )
            sanitized_evidences.append(sanitized_ev)

        bundle = LifecycleEvidenceBundle(tenant_id=tenant_id, title=title, evidences=sanitized_evidences)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def finalize_bundle(self, bundle_id: str, tenant_id: str) -> LifecycleEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            raise KeyError(f"Evidence bundle '{bundle_id}' not found.")
        if tenant_id != "global" and bundle.tenant_id != "global" and tenant_id != bundle.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, bundle.tenant_id)

        if bundle.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableLifecycleRecordException(bundle_id)

        fp = FingerprintGenerator.generate(bundle.model_dump(exclude={"immutable_record"}))
        ImmutableResourceValidator.finalize(bundle.immutable_record, fingerprint=fp)
        return bundle
