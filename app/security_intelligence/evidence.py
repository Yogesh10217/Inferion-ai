"""Security Evidence References Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.security_intelligence.exceptions import CrossTenantSecurityAccessException, ImmutableSecurityRecordException


class SecurityEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"evid_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source: str
    content_reference: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sha256_hash: str = ""


class SecurityEvidenceIntegrity(BaseModel):
    is_valid: bool = True
    sha256_hash: str = ""


class SecurityEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"evb_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    evidences: List[SecurityEvidence] = Field(default_factory=list)
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(
                resource_id=self.bundle_id,
                tenant_id=self.tenant_id,
            )


class SecurityEvidenceManager:
    """Manages security evidence bundles with SHA-256 integrity and immutable finalization."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._bundles: Dict[str, SecurityEvidenceBundle] = {}

    def create_evidence_bundle(
        self,
        tenant_id: str,
        title: str,
        evidences: List[SecurityEvidence],
    ) -> SecurityEvidenceBundle:
        sanitized_evidences = []
        for ev in evidences:
            sanitized_meta = self.sanitizer.sanitize_copy(ev.metadata)
            fp = FingerprintGenerator.generate({"source": ev.source, "ref": ev.content_reference, "meta": sanitized_meta})
            sanitized_ev = SecurityEvidence(
                tenant_id=tenant_id,
                source=ev.source,
                content_reference=ev.content_reference,
                metadata=sanitized_meta,
                sha256_hash=fp,
            )
            sanitized_evidences.append(sanitized_ev)

        bundle = SecurityEvidenceBundle(
            tenant_id=tenant_id,
            title=title,
            evidences=sanitized_evidences,
        )
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def finalize_evidence_bundle(self, bundle_id: str, tenant_id: str) -> SecurityEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            raise KeyError(f"Evidence bundle '{bundle_id}' not found.")
        if tenant_id != "global" and bundle.tenant_id != "global" and tenant_id != bundle.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, bundle.tenant_id)

        if bundle.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableSecurityRecordException(bundle_id)

        fp = FingerprintGenerator.generate(bundle.model_dump(exclude={"immutable_record"}))
        ImmutableResourceValidator.finalize(bundle.immutable_record, fingerprint=fp)
        return bundle
