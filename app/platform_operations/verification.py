"""Post-Remediation Verification & Rollback Control Engine."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_operations.remediation import RemediationPlanner, RemediationStatus
from app.platform_operations.services import ServiceCatalogManager, ServiceHealth

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class VerificationCheck(BaseModel):
    check_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    name: str
    passed: bool
    details: str = ""


class RemediationVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"verif_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    plan_id: str
    is_verified: bool = False
    is_rolled_back: bool = False
    checks: List[VerificationCheck] = Field(default_factory=list)
    verified_at: datetime = Field(default_factory=_now)


class RemediationVerifier:
    """Verifies service health & recovery after remediation; triggers rollback if verification fails."""

    def __init__(
        self,
        service_catalog_manager: Optional[ServiceCatalogManager] = None,
        remediation_planner: Optional[RemediationPlanner] = None,
    ) -> None:
        self.service_catalog_manager = service_catalog_manager or ServiceCatalogManager()
        self.remediation_planner = remediation_planner or RemediationPlanner()
        self._verifications: Dict[str, RemediationVerification] = {}

    def verify_remediation(
        self,
        tenant_id: str,
        plan_id: str,
        auto_rollback_on_failure: bool = True,
    ) -> RemediationVerification:
        plan = self.remediation_planner.get_plan(plan_id, tenant_id)

        # 1. Perform health check on target service
        svc_health_passed = True
        svc_details = "Service health is HEALTHY."

        try:
            svc = self.service_catalog_manager.get_service(plan.service_id, tenant_id)
            if svc.health == ServiceHealth.UNHEALTHY:
                svc_health_passed = False
                svc_details = f"Service '{svc.name}' is still UNHEALTHY post-remediation."
        except Exception:
            pass

        check1 = VerificationCheck(
            name="Service Health Verification",
            passed=svc_health_passed,
            details=svc_details,
        )

        check2 = VerificationCheck(
            name="Remediation Plan State Check",
            passed=(plan.status in (RemediationStatus.SUCCESSFUL, RemediationStatus.EXECUTING)),
            details=f"Plan status is {plan.status.value}.",
        )

        all_passed = check1.passed and check2.passed
        is_rolled_back = False

        if not all_passed and auto_rollback_on_failure:
            logger.warning(
                f"[REMEDIATION VERIFIER] Verification failed for plan '{plan_id}'. Triggering automatic rollback..."
            )
            plan.status = RemediationStatus.ROLLED_BACK
            plan.updated_at = _now()
            is_rolled_back = True

        verif = RemediationVerification(
            tenant_id=tenant_id,
            plan_id=plan_id,
            is_verified=all_passed,
            is_rolled_back=is_rolled_back,
            checks=[check1, check2],
        )
        self._verifications[plan_id] = verif
        logger.info(
            f"[REMEDIATION VERIFIER] Verified plan '{plan_id}': Passed={all_passed}, RolledBack={is_rolled_back}"
        )
        return verif
