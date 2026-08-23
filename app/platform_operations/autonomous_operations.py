"""Bounded Autonomous Operations Engine."""

from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.platform_operations.exceptions import AutonomousActionDeniedException
from app.platform_operations.remediation import RemediationPlan, RemediationPlanner, RemediationStrategy, RemediationStatus
from app.governance_platform.risk import RiskLevel

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AutonomyLevel(str, Enum):
    MANUAL = "MANUAL"
    ASSISTED = "ASSISTED"
    SUPERVISED = "SUPERVISED"
    CONSTRAINED_AUTONOMOUS = "CONSTRAINED_AUTONOMOUS"


class AutonomousActionPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"autopol_{uuid.uuid4().hex[:8]}")
    tenant_id: str = "global"
    allowed_strategies: List[RemediationStrategy] = Field(default_factory=lambda: [RemediationStrategy.RETRY, RemediationStrategy.RESTART, RemediationStrategy.FALLBACK])
    max_allowed_risk: RiskLevel = RiskLevel.LOW
    timeout_seconds: int = 300
    is_active: bool = True


class AutonomousOperation(BaseModel):
    operation_id: str = Field(default_factory=lambda: f"auto_op_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    plan_id: str
    autonomy_level: AutonomyLevel = AutonomyLevel.CONSTRAINED_AUTONOMOUS
    executed_at: datetime = Field(default_factory=_now)
    completed_at: Optional[datetime] = None
    status: str = "EXECUTED"
    evidence: List[str] = Field(default_factory=list)


class AutonomousOperationsEngine:
    """Executes policy-bounded autonomous operational actions with strict containment & audit logs."""

    def __init__(self, remediation_planner: Optional[RemediationPlanner] = None) -> None:
        self.remediation_planner = remediation_planner or RemediationPlanner()
        self._policies: Dict[str, AutonomousActionPolicy] = {}
        self._operations: Dict[str, AutonomousOperation] = {}

    def register_policy(self, policy: AutonomousActionPolicy) -> AutonomousActionPolicy:
        self._policies[policy.tenant_id] = policy
        logger.info(f"[AUTONOMOUS OPERATIONS] Registered policy for tenant '{policy.tenant_id}' (Max risk: {policy.max_allowed_risk.value})")
        return policy

    def execute_autonomous_remediation(
        self,
        tenant_id: str,
        plan_id: str,
        autonomy_level: AutonomyLevel = AutonomyLevel.CONSTRAINED_AUTONOMOUS,
    ) -> AutonomousOperation:
        plan = self.remediation_planner.get_plan(plan_id, tenant_id)

        # Get policy for tenant
        policy = self._policies.get(tenant_id) or AutonomousActionPolicy(tenant_id=tenant_id)

        if not policy.is_active:
            raise AutonomousActionDeniedException(f"Autonomous operations policy is inactive for tenant '{tenant_id}'.")

        # 1. Enforce max allowed risk
        if plan.overall_risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) and policy.max_allowed_risk in (RiskLevel.LOW, RiskLevel.MEDIUM):
            raise AutonomousActionDeniedException(
                f"Autonomous execution denied: Plan overall risk is {plan.overall_risk_level.value}, but policy max allowed risk is {policy.max_allowed_risk.value}. Approval is required."
            )

        # 2. Enforce allowed strategies
        for step in plan.steps:
            if step.strategy not in policy.allowed_strategies and plan.overall_risk_level != RiskLevel.LOW:
                raise AutonomousActionDeniedException(
                    f"Autonomous execution denied: Strategy '{step.strategy.value}' is not permitted by autonomous policy."
                )

        # Execute remediation plan
        executed_plan = self.remediation_planner.execute_remediation_plan(plan_id=plan_id, tenant_id=tenant_id)

        op = AutonomousOperation(
            tenant_id=tenant_id,
            plan_id=plan_id,
            autonomy_level=autonomy_level,
            completed_at=_now(),
            status="SUCCESSFUL",
            evidence=[
                f"Policy '{policy.policy_id}' validated risk {plan.overall_risk_level.value}.",
                f"Executed {len(plan.steps)} steps under level {autonomy_level.value}.",
            ],
        )
        self._operations[op.operation_id] = op
        logger.info(f"[AUTONOMOUS OPERATIONS] Autonomous operation '{op.operation_id}' completed for plan '{plan_id}'")
        return op
