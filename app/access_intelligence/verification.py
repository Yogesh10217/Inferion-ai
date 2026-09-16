"""Access Action Verification (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class VerificationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    IN_PROGRESS = "IN_PROGRESS"


class VerificationCheck(BaseModel):
    """Specific assertion check performed during verification."""
    check_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    target_resource_id: str
    expected_state: str
    observed_state: str
    passed: bool


class AccessVerification(BaseModel):
    """Access Action Verification Result."""
    verification_id: str = Field(default_factory=lambda: f"verif_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    remediation_plan_id: str
    status: VerificationStatus
    checks: List[VerificationCheck] = Field(default_factory=list)
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""


class AccessVerificationManager:
    """Verifies external state changes produced by delegated access actions."""

    def __init__(self) -> None:
        self._verifications: Dict[str, AccessVerification] = {}

    def verify_remediation(
        self,
        tenant_id: str,
        remediation_plan_id: str,
        checks: List[VerificationCheck],
        notes: str = "",
    ) -> AccessVerification:
        all_passed = all(c.passed for c in checks) if checks else False
        status = VerificationStatus.SUCCESS if all_passed else VerificationStatus.FAILURE

        verif = AccessVerification(
            tenant_id=tenant_id,
            remediation_plan_id=remediation_plan_id,
            status=status,
            checks=checks,
            notes=notes,
        )
        self._verifications[verif.verification_id] = verif
        return verif

    def get_verification(self, tenant_id: str, verification_id: str) -> AccessVerification:
        verif = self._verifications.get(verification_id)
        if not verif or verif.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return verif

    def list_verifications(self, tenant_id: str) -> List[AccessVerification]:
        return [v for v in self._verifications.values() if v.tenant_id == tenant_id]
