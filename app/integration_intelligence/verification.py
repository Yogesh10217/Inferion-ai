"""Integration Outcome Verification (Phase 5.40)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class VerificationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    IN_PROGRESS = "IN_PROGRESS"


class VerificationCheck(BaseModel):
    check_id: str = Field(default_factory=lambda: f"vchk_{uuid.uuid4().hex[:8]}")
    target_system_id: str
    expected_status_code: int = 200
    observed_status_code: int = 200
    passed: bool = True
    is_destructive_action: bool = False


class IntegrationVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"verif_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    execution_id: str
    status: VerificationStatus = VerificationStatus.SUCCESS
    checks: List[VerificationCheck] = Field(default_factory=list)
    auto_retry_allowed: bool = True
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""


class IntegrationVerificationManager:
    """Verifies integration execution outcomes and enforces verification safety rules."""

    def __init__(self) -> None:
        self._verifications: Dict[str, IntegrationVerification] = {}

    def verify_execution(
        self,
        tenant_id: str,
        execution_id: str,
        checks: List[VerificationCheck],
        notes: str = "",
    ) -> IntegrationVerification:
        all_passed = all(c.passed for c in checks) if checks else True
        status = VerificationStatus.SUCCESS if all_passed else VerificationStatus.FAILURE

        # Verification failure MUST NOT automatically retry destructive actions!
        has_destructive = any(c.is_destructive_action for c in checks)
        auto_retry_allowed = not (not all_passed and has_destructive)

        verif = IntegrationVerification(
            tenant_id=tenant_id,
            execution_id=execution_id,
            status=status,
            checks=checks,
            auto_retry_allowed=auto_retry_allowed,
            notes=notes,
        )
        self._verifications[verif.verification_id] = verif
        return verif

    def get_verification(self, tenant_id: str, verification_id: str) -> IntegrationVerification:
        verif = self._verifications.get(verification_id)
        if not verif or verif.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return verif

    def list_verifications(self, tenant_id: str) -> List[IntegrationVerification]:
        return [v for v in self._verifications.values() if v.tenant_id == tenant_id]
