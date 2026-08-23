"""Human & Automated Compliance Attestations Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import AttestationExpiredException, CrossTenantComplianceAccessException


class AttestationType(str, Enum):
    MANUAL = "MANUAL"
    AUTOMATED = "AUTOMATED"
    HYBRID = "HYBRID"


class AttestationStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class ComplianceAttestation(BaseModel):
    attestation_id: str = Field(default_factory=lambda: f"attest_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    attestation_type: AttestationType = AttestationType.MANUAL
    status: AttestationStatus = AttestationStatus.APPROVED
    attested_by: str = "compliance_officer"
    statement: str
    valid_from: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=90))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.valid_until


class AttestationManager:
    """Manages compliance attestation lifecycle and handles expiration signals."""

    def __init__(self) -> None:
        self._attestations: Dict[str, ComplianceAttestation] = {}

    def submit_attestation(
        self,
        tenant_id: str,
        control_id: str,
        statement: str,
        attested_by: str = "compliance_officer",
        valid_days: int = 90,
    ) -> ComplianceAttestation:
        now = datetime.now(timezone.utc)
        att = ComplianceAttestation(
            tenant_id=tenant_id,
            control_id=control_id,
            statement=statement,
            attested_by=attested_by,
            valid_from=now,
            valid_until=now + timedelta(days=valid_days),
            status=AttestationStatus.APPROVED,
        )
        self._attestations[att.attestation_id] = att
        return att

    def get_attestation(self, attestation_id: str, tenant_id: str) -> ComplianceAttestation:
        att = self._attestations.get(attestation_id)
        if not att:
            raise KeyError(f"Attestation '{attestation_id}' not found.")
        if att.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=att.tenant_id, resource_id=attestation_id)
        if att.is_expired():
            att.status = AttestationStatus.EXPIRED
            raise AttestationExpiredException(attestation_id=attestation_id, tenant_id=tenant_id)
        return att

    def expire_attestation_explicitly(self, attestation_id: str, tenant_id: str) -> ComplianceAttestation:
        att = self.get_attestation(attestation_id, tenant_id)
        att.valid_until = datetime.now(timezone.utc) - timedelta(seconds=1)
        att.status = AttestationStatus.EXPIRED
        return att

    def list_attestations(self, tenant_id: str) -> List[ComplianceAttestation]:
        return [a for a in self._attestations.values() if a.tenant_id == tenant_id]
