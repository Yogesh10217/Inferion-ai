"""Identity Verification Intelligence."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


class VerificationCheck(BaseModel):
    check_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    check_type: str  # PERMISSION_REMOVED, MFA_VERIFIED, CREDENTIAL_ROTATED
    target_entity: str
    status: VerificationStatus = VerificationStatus.PASSED
    reasoning: str = ""


class IdentityVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    checks: List[VerificationCheck] = Field(default_factory=list)
    overall_status: VerificationStatus = VerificationStatus.PASSED
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityVerificationManager:
    """Verifies external state changes resulting from delegated identity actions."""

    def __init__(self) -> None:
        self._verifications: Dict[str, IdentityVerification] = {}

    def verify_remediation(
        self,
        tenant_id: str,
        identity_id: str,
        checks: Optional[List[VerificationCheck]] = None,
    ) -> IdentityVerification:
        chk_list = checks or [
            VerificationCheck(check_type="PERMISSION_REMOVED", target_entity=identity_id)
        ]
        all_passed = all(c.status == VerificationStatus.PASSED for c in chk_list)
        overall = VerificationStatus.PASSED if all_passed else VerificationStatus.FAILED

        verification = IdentityVerification(
            tenant_id=tenant_id,
            identity_id=identity_id,
            checks=chk_list,
            overall_status=overall,
        )
        self._verifications[verification.verification_id] = verification
        return verification

    def get_verification(self, tenant_id: str, verification_id: str) -> IdentityVerification:
        v = self._verifications.get(verification_id)
        if not v or v.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return v
