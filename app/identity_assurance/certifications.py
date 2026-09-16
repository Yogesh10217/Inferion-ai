"""Identity Certification Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class CertificationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    REJECTED = "REJECTED"


class CertificationScope(BaseModel):
    roles_certified: List[str] = Field(default_factory=list)
    permissions_certified: List[str] = Field(default_factory=list)


class IdentityCertification(BaseModel):
    certification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    certified_by: str = "security_manager"
    scope: CertificationScope = Field(default_factory=CertificationScope)
    status: CertificationStatus = CertificationStatus.ACTIVE
    certified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CertificationAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    is_certified: bool = True
    active_certifications_count: int = 1
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityCertificationManager:
    """Manages identity access certifications."""

    def __init__(self) -> None:
        self._certifications: Dict[str, IdentityCertification] = {}

    def certify_identity(
        self,
        tenant_id: str,
        identity_id: str,
        certified_by: str = "security_manager",
        roles: Optional[List[str]] = None,
    ) -> IdentityCertification:
        scope = CertificationScope(roles_certified=roles or ["Developer"])
        cert = IdentityCertification(
            tenant_id=tenant_id,
            identity_id=identity_id,
            certified_by=certified_by,
            scope=scope,
        )
        self._certifications[cert.certification_id] = cert
        return cert

    def get_certification(self, tenant_id: str, certification_id: str) -> IdentityCertification:
        cert = self._certifications.get(certification_id)
        if not cert or cert.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return cert

    def assess_certification(self, tenant_id: str, identity_id: str) -> CertificationAssessment:
        active_certs = [
            c for c in self._certifications.values()
            if c.tenant_id == tenant_id and c.identity_id == identity_id and c.status == CertificationStatus.ACTIVE
        ]
        return CertificationAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            is_certified=len(active_certs) > 0,
            active_certifications_count=len(active_certs),
        )
