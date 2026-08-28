"""Control Attestation and Assurance Declaration Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.control_assurance.exceptions import (
    ControlAttestationException,
    ImmutableAssuranceRecordException,
    CrossTenantControlAssuranceAccessException,
)


class AttestationStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    ATTESTED = "ATTESTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class AttestationScope(BaseModel):
    scope_type: str = "TENANT"
    scope_target_id: str


class AttestationEvidence(BaseModel):
    evidence_bundle_id: str
    checksum_sha256: str


class ControlAttestation(BaseModel):
    attestation_id: str = Field(default_factory=lambda: f"att_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    status: AttestationStatus = AttestationStatus.DRAFT
    scope: AttestationScope
    attestor_id: Optional[str] = None
    fingerprint_sha256: str = ""
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlAttestationManager:
    """Manages control attestation declaration and fingerprinting."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._attestations: Dict[str, ControlAttestation] = {}

    def create_attestation(self, tenant_id: str, control_id: str, scope_target_id: str) -> ControlAttestation:
        att = ControlAttestation(
            tenant_id=tenant_id,
            control_id=control_id,
            scope=AttestationScope(scope_target_id=scope_target_id),
        )
        self._attestations[att.attestation_id] = att
        return att

    def finalize_attestation(self, attestation_id: str, tenant_id: str, attestor_id: str) -> ControlAttestation:
        att = self._attestations.get(attestation_id)
        if not att:
            raise ControlAttestationException(attestation_id, "Attestation record not found.")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, att.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()

        if att.is_finalized:
            raise ImmutableAssuranceRecordException(f"Attestation '{attestation_id}' is finalized and immutable.")

        att.attestor_id = attestor_id
        att.status = AttestationStatus.ATTESTED
        att.is_finalized = True
        att.fingerprint_sha256 = FingerprintGenerator.generate(
            {"attestation_id": attestation_id, "tenant_id": tenant_id, "attestor_id": attestor_id}, "1.0.0"
        )
        return att
