"""Delegated Financial Action Verification (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class VerificationCheck(BaseModel):
    check_id: str = Field(default_factory=lambda: f"chk_fin_{uuid.uuid4().hex[:8]}")
    check_name: str
    passed: bool = True
    details: str = ""


class FinOpsVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"verif_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    delegation_plan_id: str
    is_verified: bool = True
    checks: List[VerificationCheck] = Field(default_factory=list)
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsVerificationManager:
    """Verifies operational outcomes post-delegated financial execution."""

    def __init__(self) -> None:
        self._verifications: Dict[str, FinOpsVerification] = {}

    def verify_action(
        self,
        tenant_id: str,
        delegation_plan_id: str,
        checks: List[VerificationCheck],
    ) -> FinOpsVerification:
        all_passed = all(c.passed for c in checks)
        verif = FinOpsVerification(
            tenant_id=tenant_id,
            delegation_plan_id=delegation_plan_id,
            is_verified=all_passed,
            checks=checks,
        )
        self._verifications[verif.verification_id] = verif
        return verif

    def get_verification(self, tenant_id: str, verification_id: str) -> FinOpsVerification:
        verif = self._verifications.get(verification_id)
        if not verif or verif.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return verif
