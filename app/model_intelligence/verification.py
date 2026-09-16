"""Remediation Verification for Model Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


class VerificationCheck(BaseModel):
    check_name: str
    target: str  # rollback_effectiveness, performance_recovery, safety_improvement, drift_resolution, reliability_recovery
    passed: bool = True
    details: str = ""


class ModelVerification(BaseModel):
    verification_id: str
    remediation_plan_id: str
    model_id: str
    tenant_id: str
    status: VerificationStatus = VerificationStatus.PENDING
    checks: List[VerificationCheck] = Field(default_factory=list)
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelVerificationManager:
    """Verifies external remediation execution and effectiveness."""

    def __init__(self) -> None:
        self._verifications: Dict[str, ModelVerification] = {}

    def verify_remediation(
        self,
        remediation_plan_id: str,
        model_id: str,
        tenant_id: str,
        checks: List[VerificationCheck],
    ) -> ModelVerification:
        v_id = f"mver-{uuid.uuid4().hex[:8]}"
        all_passed = all(c.passed for c in checks)
        status = VerificationStatus.PASSED if all_passed else VerificationStatus.FAILED

        verification = ModelVerification(
            verification_id=v_id,
            remediation_plan_id=remediation_plan_id,
            model_id=model_id,
            tenant_id=tenant_id,
            status=status,
            checks=checks,
        )

        self._verifications[v_id] = verification
        logger.info(f"[MODEL VERIFICATION] Verification {v_id} for plan {remediation_plan_id} -> {status}")
        return verification

    def get_verification(self, verification_id: str, tenant_id: str) -> ModelVerification:
        v = self._verifications.get(verification_id)
        if not v:
            raise ValueError(f"Verification record '{verification_id}' not found.")
        if v.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return v
