"""Access Certification Governance (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
import hashlib
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import (
    AccessCertificationNotFoundException,
    CrossTenantAccessIntelligenceException,
    InvalidAccessStateTransitionException,
    ImmutableAccessRecordException,
)


class CertificationScope(str, Enum):
    ENTERPRISE = "ENTERPRISE"
    DEPT = "DEPT"
    SYSTEM = "SYSTEM"
    ROLE_CATALOG = "ROLE_CATALOG"


class CertificationStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FINALIZED = "FINALIZED"


class CertificationDecision(str, Enum):
    CERTIFIED = "CERTIFIED"
    REVOCATION_REQUIRED = "REVOCATION_REQUIRED"
    EXCEPTION_GRANTED = "EXCEPTION_GRANTED"


class AccessCertification(BaseModel):
    """Access Certification representation."""
    certification_id: str = Field(default_factory=lambda: f"cert_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    certifier_identity_id: str
    scope: CertificationScope = CertificationScope.ENTERPRISE
    status: CertificationStatus = CertificationStatus.DRAFT
    decision: Optional[CertificationDecision] = None
    fingerprint: str = ""
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessCertificationManager:
    """Access Certification Governance Manager."""

    def __init__(self) -> None:
        self._certifications: Dict[str, AccessCertification] = {}

    def create_certification(
        self,
        tenant_id: str,
        name: str,
        certifier_identity_id: str,
        scope: CertificationScope = CertificationScope.ENTERPRISE,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessCertification:
        cert = AccessCertification(
            tenant_id=tenant_id,
            name=name,
            certifier_identity_id=certifier_identity_id,
            scope=scope,
            metadata=metadata or {},
        )
        self._certifications[cert.certification_id] = cert
        return cert

    def start_certification(self, tenant_id: str, certification_id: str) -> AccessCertification:
        cert = self.get_certification(tenant_id, certification_id)
        if cert.status != CertificationStatus.DRAFT:
            raise InvalidAccessStateTransitionException(cert.status.value, CertificationStatus.IN_PROGRESS.value)
        cert.status = CertificationStatus.IN_PROGRESS
        return cert

    def record_decision(self, tenant_id: str, certification_id: str, decision: CertificationDecision) -> AccessCertification:
        cert = self.get_certification(tenant_id, certification_id)
        if cert.is_finalized:
            raise ImmutableAccessRecordException(certification_id)
        cert.decision = decision
        cert.status = CertificationStatus.COMPLETED
        return cert

    def finalize_certification(self, tenant_id: str, certification_id: str) -> AccessCertification:
        cert = self.get_certification(tenant_id, certification_id)
        if cert.status not in [CertificationStatus.COMPLETED, CertificationStatus.IN_PROGRESS]:
            raise InvalidAccessStateTransitionException(cert.status.value, CertificationStatus.FINALIZED.value)
        cert.status = CertificationStatus.FINALIZED
        cert.is_finalized = True
        cert.finalized_at = datetime.now(timezone.utc)
        
        # Calculate SHA-256 fingerprint for immutable certification record
        raw_data = f"{cert.certification_id}:{cert.tenant_id}:{cert.decision}:{cert.finalized_at.isoformat()}"
        cert.fingerprint = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()
        return cert

    def get_certification(self, tenant_id: str, certification_id: str) -> AccessCertification:
        cert = self._certifications.get(certification_id)
        if not cert or cert.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return cert

    def list_certifications(self, tenant_id: str, status: Optional[CertificationStatus] = None) -> List[AccessCertification]:
        results = [c for c in self._certifications.values() if c.tenant_id == tenant_id]
        if status:
            results = [c for c in results if c.status == status]
        return results
