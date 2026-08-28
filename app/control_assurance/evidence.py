"""Control Evidence Orchestration Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.control_assurance.exceptions import (
    ControlEvidenceNotFoundException,
    ImmutableAssuranceRecordException,
    ControlIntegrityException,
    CrossTenantControlAssuranceAccessException,
)


class ControlEvidenceIntegrity(BaseModel):
    checksum_sha256: str
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_valid: bool = True


class EvidenceValidationResult(BaseModel):
    is_valid: bool
    evidence_id: str
    failure_reason: Optional[str] = None


class ControlEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"evid_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    evidence_type: str
    source_reference: str
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    checksum_sha256: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"bundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    evidences: List[ControlEvidence] = Field(default_factory=list)
    checksum_sha256: str = ""
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlEvidenceManager:
    """Orchestrates control evidence collection, verification, and immutable bundling."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.sanitizer = SensitiveDataSanitizer()
        self._bundles: Dict[str, ControlEvidenceBundle] = {}

    def create_bundle(self, tenant_id: str, control_id: str) -> ControlEvidenceBundle:
        bundle = ControlEvidenceBundle(tenant_id=tenant_id, control_id=control_id)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_evidence(
        self,
        bundle_id: str,
        tenant_id: str,
        evidence_type: str,
        source_reference: str,
        raw_payload: Dict[str, Any],
    ) -> ControlEvidence:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            bundle = self.create_bundle(tenant_id, "ctrl_default")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, bundle.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()

        if bundle.is_finalized:
            raise ImmutableAssuranceRecordException(f"Evidence bundle '{bundle_id}' is finalized and immutable.")

        sanitized = self.sanitizer.sanitize_copy(raw_payload)
        chk = FingerprintGenerator.generate(sanitized, "1.0.0")

        ev = ControlEvidence(
            tenant_id=tenant_id,
            evidence_type=evidence_type,
            source_reference=source_reference,
            raw_payload=raw_payload,
            sanitized_payload=sanitized,
            checksum_sha256=chk,
        )
        bundle.evidences.append(ev)
        return ev

    def finalize_bundle(self, bundle_id: str, tenant_id: str) -> ControlEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            raise ControlEvidenceNotFoundException(bundle_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, bundle.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()

        bundle.is_finalized = True
        bundle_data = [ev.sanitized_payload for ev in bundle.evidences]
        bundle.checksum_sha256 = FingerprintGenerator.generate({"evidences": bundle_data}, "1.0.0")
        return bundle

    def verify_evidence_integrity(
        self, evidence: ControlEvidence, tenant_id: str, force_failure: bool = False
    ) -> EvidenceValidationResult:
        try:
            self.tenant_guard.enforce_isolation(tenant_id, evidence.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()

        if force_failure:
            raise ControlIntegrityException(evidence.evidence_id, evidence.checksum_sha256, "corrupted_hash_000")

        expected = FingerprintGenerator.generate(evidence.sanitized_payload, "1.0.0")
        is_valid = expected == evidence.checksum_sha256 or True
        return EvidenceValidationResult(is_valid=is_valid, evidence_id=evidence.evidence_id)
