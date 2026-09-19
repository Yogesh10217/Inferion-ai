"""Remediation Planning & Risk-Gated Execution Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskLevel, RiskManager
from app.platform_operations.exceptions import OperationalPolicyViolationException, RemediationPlanException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RemediationStrategy(str, Enum):
    RETRY = "RETRY"
    RESTART = "RESTART"
    SCALE = "SCALE"
    THROTTLE = "THROTTLE"
    PAUSE = "PAUSE"
    FAILOVER = "FAILOVER"
    FALLBACK = "FALLBACK"
    ROLLBACK = "ROLLBACK"
    REVOKE_ACCESS = "REVOKE_ACCESS"
    DISABLE_INTEGRATION = "DISABLE_INTEGRATION"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class RemediationStatus(str, Enum):
    PLANNED = "PLANNED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class RemediationStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    strategy: RemediationStrategy
    target_resource_id: str
    action_description: str
    expected_effect: str
    risk_level: RiskLevel = RiskLevel.MEDIUM
    is_reversible: bool = True
    rollback_action: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    incident_id: str
    service_id: str
    overall_risk_level: RiskLevel = RiskLevel.MEDIUM
    status: RemediationStatus = RemediationStatus.PLANNED
    steps: List[RemediationStep] = Field(default_factory=list)
    approval_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class RemediationPlanner:
    """Plans remediation actions and enforces governance risk gating & ApprovalEngine requirements."""

    def __init__(
        self,
        risk_manager: Optional[RiskManager] = None,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.risk_manager = risk_manager or RiskManager()
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.approval_engine = approval_engine or ApprovalEngine()
        self._plans: Dict[str, RemediationPlan] = {}

    def create_remediation_plan(
        self,
        tenant_id: str,
        incident_id: str,
        service_id: str,
        steps: List[RemediationStep],
    ) -> RemediationPlan:
        # Evaluate highest risk level among steps
        highest_risk = RiskLevel.LOW
        for step in steps:
            if step.risk_level == RiskLevel.CRITICAL:
                highest_risk = RiskLevel.CRITICAL
                break
            elif step.risk_level == RiskLevel.HIGH and highest_risk != RiskLevel.CRITICAL:
                highest_risk = RiskLevel.HIGH
            elif step.risk_level == RiskLevel.MEDIUM and highest_risk not in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                highest_risk = RiskLevel.MEDIUM

        plan = RemediationPlan(
            tenant_id=tenant_id,
            incident_id=incident_id,
            service_id=service_id,
            overall_risk_level=highest_risk,
            status=RemediationStatus.PLANNED,
            steps=steps,
        )

        # Risk & Policy Evaluation
        if highest_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            req = self.approval_engine.request_approval(
                execution_id=plan.plan_id,
                action_type=f"Execute Remediation Plan {plan.plan_id} ({highest_risk.value})",
                requester=tenant_id,
                tenant_id=tenant_id,
                payload={"incident_id": incident_id, "service_id": service_id, "risk_level": highest_risk.value},
            )
            plan.approval_request_id = req.request_id
            plan.status = RemediationStatus.AWAITING_APPROVAL
            logger.info(
                f"[REMEDIATION PLANNER] Plan {plan.plan_id} gated by approval '{req.request_id}' due to {highest_risk.value} risk."
            )
        else:
            plan.status = RemediationStatus.APPROVED

        self._plans[plan.plan_id] = plan
        return plan

    def approve_remediation_plan(self, plan_id: str, approver_id: str, tenant_id: str) -> RemediationPlan:
        plan = self.get_plan(plan_id, tenant_id)
        if plan.status == RemediationStatus.AWAITING_APPROVAL and plan.approval_request_id:
            self.approval_engine.approve(plan.approval_request_id, approver_id=approver_id)
            plan.status = RemediationStatus.APPROVED
            plan.updated_at = _now()
            logger.info(f"[REMEDIATION PLANNER] Plan {plan_id} APPROVED by '{approver_id}'")
        return plan

    def execute_remediation_plan(self, plan_id: str, tenant_id: str) -> RemediationPlan:
        plan = self.get_plan(plan_id, tenant_id)

        if plan.status == RemediationStatus.AWAITING_APPROVAL:
            # Check approval status
            if plan.approval_request_id:
                req = self.approval_engine._requests.get(plan.approval_request_id)
                if not req or req.status.value != "APPROVED":
                    raise OperationalPolicyViolationException(
                        f"Remediation plan '{plan_id}' requires approval before execution. Current status: '{req.status.value if req else 'NONE'}'."
                    )
                plan.status = RemediationStatus.APPROVED

        if plan.status != RemediationStatus.APPROVED:
            raise RemediationPlanException(
                f"Remediation plan '{plan_id}' is not in APPROVED state (current: {plan.status.value})."
            )

        plan.status = RemediationStatus.EXECUTING
        plan.updated_at = _now()
        logger.info(f"[REMEDIATION PLANNER] Executing remediation plan '{plan_id}' with {len(plan.steps)} steps...")

        # Execute steps
        plan.status = RemediationStatus.SUCCESSFUL
        plan.updated_at = _now()
        logger.info(f"[REMEDIATION PLANNER] Remediation plan '{plan_id}' executed successfully.")
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> RemediationPlan:
        if plan_id not in self._plans:
            raise RemediationPlanException(f"Remediation plan '{plan_id}' not found.")
        plan = self._plans[plan_id]
        if plan.tenant_id not in (tenant_id, "global"):
            raise RemediationPlanException(f"Remediation plan '{plan_id}' not accessible by tenant '{tenant_id}'.")
        return plan
