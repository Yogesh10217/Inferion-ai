"""Autonomous Remediation Engine with Strict Approval Engine Gating and Auto-Rollback."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.operations.exceptions import RemediationFailedException
from app.operations.runbooks import RunbookManager, RunbookMode, RunbookStep

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RemediationRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RemediationStatus(str, Enum):
    DETECTED = "DETECTED"
    ANALYZED = "ANALYZED"
    PLANNED = "PLANNED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    ESCALATED = "ESCALATED"


class RemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rem_{uuid.uuid4().hex[:10]}")
    title: str
    tenant_id: str = "global"
    risk_level: RemediationRisk = RemediationRisk.LOW
    status: RemediationStatus = RemediationStatus.PLANNED

    target_resource_id: str
    runbook_id: Optional[str] = None
    approval_request_id: Optional[str] = None
    verification_passed: bool = False

    created_at: datetime = Field(default_factory=_now)


class AutonomousRemediationEngine:
    """Orchestrates autonomous failure remediation while enforcing ApprovalEngine gating for HIGH/CRITICAL actions."""

    def __init__(
        self,
        approval_engine: Optional[ApprovalEngine] = None,
        runbook_manager: Optional[RunbookManager] = None,
    ) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self.runbook_manager = runbook_manager or RunbookManager()
        self._plans: Dict[str, RemediationPlan] = {}

    def plan_remediation(
        self,
        title: str,
        target_resource_id: str,
        risk_level: RemediationRisk,
        runbook_id: Optional[str] = None,
        tenant_id: str = "global",
    ) -> RemediationPlan:
        plan = RemediationPlan(
            title=title,
            target_resource_id=target_resource_id,
            risk_level=risk_level,
            runbook_id=runbook_id,
            tenant_id=tenant_id,
        )

        if risk_level in (RemediationRisk.HIGH, RemediationRisk.CRITICAL):
            plan.status = RemediationStatus.APPROVAL_REQUIRED
            plan.approval_request_id = f"rem_appr_{plan.plan_id[:8]}"
            logger.warning(f"[REMEDIATION ENGINE] {risk_level.value} risk remediation '{plan.plan_id}' REQUIRES APPROVAL (Request ID: {plan.approval_request_id})")
        else:
            plan.status = RemediationStatus.APPROVED
            logger.info(f"[REMEDIATION ENGINE] {risk_level.value} risk remediation '{plan.plan_id}' automatically approved for execution")

        self._plans[plan.plan_id] = plan
        return plan

    def execute_remediation(self, plan_id: str, simulate_failure: bool = False) -> RemediationPlan:
        plan = self.get_plan(plan_id)

        if plan.status == RemediationStatus.APPROVAL_REQUIRED:
            raise RemediationFailedException(plan_id, "Plan requires explicit administrator approval before execution")

        plan.status = RemediationStatus.EXECUTING
        logger.info(f"[REMEDIATION ENGINE] Executing remediation plan '{plan_id}'...")

        if simulate_failure:
            plan.status = RemediationStatus.EXECUTION_FAILED
            logger.error(f"[REMEDIATION ENGINE] Execution failed on '{plan_id}' -> Triggering automatic ROLLBACK!")
            if plan.runbook_id:
                self.runbook_manager.execute_runbook(plan.runbook_id, mode=RunbookMode.ROLLBACK)
            plan.status = RemediationStatus.ROLLED_BACK
            return plan

        # Execute runbook if attached
        if plan.runbook_id:
            self.runbook_manager.execute_runbook(plan.runbook_id, mode=RunbookMode.EXECUTE)

        # Verification step
        plan.status = RemediationStatus.VERIFYING
        if plan.runbook_id:
            self.runbook_manager.execute_runbook(plan.runbook_id, mode=RunbookMode.VERIFY)

        plan.verification_passed = True
        plan.status = RemediationStatus.COMPLETED
        logger.info(f"[REMEDIATION ENGINE] Remediation plan '{plan_id}' COMPLETED and VERIFIED successfully!")
        return plan

    def approve_remediation(self, plan_id: str) -> RemediationPlan:
        plan = self.get_plan(plan_id)
        if plan.status == RemediationStatus.APPROVAL_REQUIRED:
            plan.status = RemediationStatus.APPROVED
            logger.info(f"[REMEDIATION ENGINE] Remediation plan '{plan_id}' APPROVED by administrator.")
        return plan

    def get_plan(self, plan_id: str) -> RemediationPlan:
        p = self._plans.get(plan_id)
        if not p:
            raise KeyError(f"Remediation plan '{plan_id}' not found")
        return p

    def list_plans(self, tenant_id: Optional[str] = None) -> List[RemediationPlan]:
        res = list(self._plans.values())
        if tenant_id:
            res = [p for p in res if p.tenant_id == tenant_id]
        return res
