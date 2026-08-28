"""Autonomous Execution Safeguards Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.exceptions import (
    AgentExecutionBlockedException,
    AgentRuntimeLimitExceededException,
    AgentBudgetExceededException,
    HighRiskAgentActionRequiresApprovalException,
)


class SafeguardType(str, Enum):
    MAX_STEPS = "MAX_STEPS"
    MAX_COST = "MAX_COST"
    MAX_DURATION = "MAX_DURATION"
    MAX_TOOL_CALLS = "MAX_TOOL_CALLS"
    MAX_RECURSION_DEPTH = "MAX_RECURSION_DEPTH"
    RESTRICTED_ACTION = "RESTRICTED_ACTION"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    POLICY_BOUNDARY = "POLICY_BOUNDARY"


class SafeguardViolation(BaseModel):
    safeguard_type: SafeguardType
    threshold: Any
    actual: Any
    message: str


class SafeguardEvaluation(BaseModel):
    passed: bool
    triggered_safeguards: List[SafeguardType] = Field(default_factory=list)
    violations: List[SafeguardViolation] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSafeguard(BaseModel):
    safeguard_id: str = Field(default_factory=lambda: f"sg_{uuid.uuid4().hex[:10]}")
    tenant_id: str
    safeguard_type: SafeguardType
    threshold_value: Any
    is_active: bool = True


class AgentSafeguardManager:
    """Evaluates mandatory safeguards and immediately halts or escalates execution upon violation."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._safeguards: Dict[str, List[AgentSafeguard]] = {}

    def add_safeguard(
        self,
        tenant_id: str,
        safeguard_type: SafeguardType,
        threshold_value: Any,
    ) -> AgentSafeguard:
        sg = AgentSafeguard(
            tenant_id=tenant_id,
            safeguard_type=safeguard_type,
            threshold_value=threshold_value,
        )
        if tenant_id not in self._safeguards:
            self._safeguards[tenant_id] = []
        self._safeguards[tenant_id].append(sg)
        return sg

    def evaluate_safeguards(
        self,
        tenant_id: str,
        current_steps: int = 0,
        current_cost: float = 0.0,
        current_duration_sec: int = 0,
        current_tool_calls: int = 0,
        recursion_depth: int = 0,
        proposed_action: str = "",
        is_destructive: bool = False,
    ) -> SafeguardEvaluation:
        violations: List[SafeguardViolation] = []
        triggered: List[SafeguardType] = []

        # Default standard thresholds
        max_steps = 25
        max_cost = 100.0
        max_duration = 300
        max_tool_calls = 50
        max_recursion = 5

        # Check tenant overrides if present
        for sg in self._safeguards.get(tenant_id, []):
            if not sg.is_active:
                continue
            if sg.safeguard_type == SafeguardType.MAX_STEPS:
                max_steps = int(sg.threshold_value)
            elif sg.safeguard_type == SafeguardType.MAX_COST:
                max_cost = float(sg.threshold_value)
            elif sg.safeguard_type == SafeguardType.MAX_DURATION:
                max_duration = int(sg.threshold_value)

        # 1. Step safeguard
        if current_steps >= max_steps:
            triggered.append(SafeguardType.MAX_STEPS)
            violations.append(SafeguardViolation(
                safeguard_type=SafeguardType.MAX_STEPS,
                threshold=max_steps,
                actual=current_steps,
                message=f"Safeguard MAX_STEPS triggered: current {current_steps} >= limit {max_steps}."
            ))

        # 2. Cost safeguard
        if current_cost >= max_cost:
            triggered.append(SafeguardType.MAX_COST)
            violations.append(SafeguardViolation(
                safeguard_type=SafeguardType.MAX_COST,
                threshold=max_cost,
                actual=current_cost,
                message=f"Safeguard MAX_COST triggered: current ${current_cost:.2f} >= limit ${max_cost:.2f}."
            ))

        # 3. Recursion depth safeguard
        if recursion_depth >= max_recursion:
            triggered.append(SafeguardType.MAX_RECURSION_DEPTH)
            violations.append(SafeguardViolation(
                safeguard_type=SafeguardType.MAX_RECURSION_DEPTH,
                threshold=max_recursion,
                actual=recursion_depth,
                message=f"Safeguard MAX_RECURSION_DEPTH triggered: recursion depth {recursion_depth} >= limit {max_recursion}."
            ))

        # 4. Human approval required / Destructive safeguard
        if is_destructive or "DELETE" in proposed_action.upper():
            triggered.append(SafeguardType.HUMAN_APPROVAL_REQUIRED)
            violations.append(SafeguardViolation(
                safeguard_type=SafeguardType.HUMAN_APPROVAL_REQUIRED,
                threshold="HUMAN_APPROVAL",
                actual=proposed_action,
                message=f"Safeguard HUMAN_APPROVAL_REQUIRED triggered for action '{proposed_action}'."
            ))

        passed = len(violations) == 0
        eval_res = SafeguardEvaluation(
            passed=passed,
            triggered_safeguards=triggered,
            violations=violations,
        )

        if SafeguardType.MAX_STEPS in triggered or SafeguardType.MAX_RECURSION_DEPTH in triggered:
            raise AgentRuntimeLimitExceededException(violations[0].message)
        elif SafeguardType.MAX_COST in triggered:
            raise AgentBudgetExceededException(violations[0].message)
        elif SafeguardType.HUMAN_APPROVAL_REQUIRED in triggered:
            raise HighRiskAgentActionRequiresApprovalException(violations[0].message)

        return eval_res
