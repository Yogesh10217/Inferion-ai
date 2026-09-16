"""Operational Outcome Verification (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    RemediationVerificationException,
)


class VerificationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    IN_PROGRESS = "IN_PROGRESS"


class OperationalVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"verif_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    remediation_plan_id: str
    status: VerificationStatus = VerificationStatus.SUCCESS
    service_recovered: bool = True
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""


class OperationsVerificationManager:
    """Verifies operational outcomes post-delegated execution."""

    def __init__(self) -> None:
        self._verifications: Dict[str, OperationalVerification] = {}

    def verify_remediation(
        self,
        tenant_id: str,
        remediation_plan_id: str,
        service_recovered: bool = True,
        notes: str = "",
    ) -> OperationalVerification:
        status = VerificationStatus.SUCCESS if service_recovered else VerificationStatus.FAILURE
        verif = OperationalVerification(
            tenant_id=tenant_id,
            remediation_plan_id=remediation_plan_id,
            status=status,
            service_recovered=service_recovered,
            notes=notes,
        )
        self._verifications[verif.verification_id] = verif
        if not service_recovered:
            raise RemediationVerificationException(remediation_plan_id, "Service recovery check failed.")
        return verif

    def get_verification(self, tenant_id: str, verification_id: str) -> OperationalVerification:
        verif = self._verifications.get(verification_id)
        if not verif or verif.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return verif
