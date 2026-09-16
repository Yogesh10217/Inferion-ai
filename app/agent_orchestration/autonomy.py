"""Bounded Autonomy Management Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import (
    CrossTenantAgentAccessException,
)
from app.platform_contracts.tenant import TenantAccessGuard


class AgentAutonomyLevel(str, Enum):
    NONE = "NONE"                          # Fully manual / human-driven
    ASSISTED = "ASSISTED"                  # Agent recommends, human executes
    SUPERVISED = "SUPERVISED"              # Agent executes with mandatory human review before finalize
    CONDITIONAL = "CONDITIONAL"            # Agent executes within strict thresholds; approval required above threshold
    LIMITED_AUTONOMOUS = "LIMITED_AUTONOMOUS"  # Bounded execution within strict explicit boundaries


class AutonomyBoundary(BaseModel):
    max_risk_level: str = "MEDIUM"         # LOW, MEDIUM, HIGH, CRITICAL
    allowed_target_systems: List[str] = Field(default_factory=lambda: ["*"])
    allowed_data_classifications: List[str] = Field(default_factory=lambda: ["PUBLIC", "INTERNAL", "CONFIDENTIAL"])
    spending_limit_dollars: float = 100.0
    max_execution_duration_sec: int = 300
    max_steps: int = 25
    max_tool_invocations: int = 50
    prohibited_actions: List[str] = Field(default_factory=lambda: [
        "DELETE_RESOURCE",
        "MODIFY_SECURITY_POLICY",
        "GRANT_PERMISSION",
        "PRODUCE_FINANCIAL_TRANSACTION",
        "DEPLOY_TO_PRODUCTION"
    ])


class AutonomyLimit(BaseModel):
    dimension: str
    limit_value: Any
    current_value: Any


class AutonomyViolation(BaseModel):
    violation_type: str
    dimension: str
    limit_value: Any
    requested_value: Any
    message: str


class AutonomyEvaluation(BaseModel):
    is_allowed: bool
    autonomy_level: AgentAutonomyLevel
    requires_approval: bool = False
    violations: List[AutonomyViolation] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentAutonomyPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"autopoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    name: str = "Default Autonomy Policy"
    autonomy_level: AgentAutonomyLevel = AgentAutonomyLevel.SUPERVISED
    boundary: AutonomyBoundary = Field(default_factory=AutonomyBoundary)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentAutonomyManager:
    """Manages explicit autonomy boundaries and enforces runtime autonomy policy evaluation."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._policies: Dict[str, AgentAutonomyPolicy] = {}

    def set_autonomy_policy(
        self,
        tenant_id: str,
        agent_id: str,
        name: str = "Default Autonomy Policy",
        autonomy_level: AgentAutonomyLevel = AgentAutonomyLevel.SUPERVISED,
        boundary: Optional[AutonomyBoundary] = None,
        policy_id: Optional[str] = None,
    ) -> AgentAutonomyPolicy:
        pid = policy_id or f"autopoly_{uuid.uuid4().hex[:12]}"
        policy = AgentAutonomyPolicy(
            policy_id=pid,
            tenant_id=tenant_id,
            agent_id=agent_id,
            name=name,
            autonomy_level=autonomy_level,
            boundary=boundary or AutonomyBoundary(),
        )
        self._policies[policy.policy_id] = policy
        return policy

    def get_autonomy_policy(self, policy_id: str, tenant_id: str) -> AgentAutonomyPolicy:
        policy = self._policies.get(policy_id)
        if not policy:
            # Fallback default
            return AgentAutonomyPolicy(policy_id=policy_id, tenant_id=tenant_id, agent_id="default")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, policy.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, policy.tenant_id)

        return policy

    def evaluate_action_autonomy(
        self,
        policy: AgentAutonomyPolicy,
        proposed_action: str,
        target_system: str,
        risk_level: str = "LOW",
        cost_dollars: float = 0.0,
        estimated_steps: int = 1,
        data_classification: str = "INTERNAL",
    ) -> AutonomyEvaluation:
        violations = []
        requires_approval = False

        # 1. Level check
        if policy.autonomy_level == AgentAutonomyLevel.NONE:
            requires_approval = True
            violations.append(AutonomyViolation(
                violation_type="AUTONOMY_LEVEL_ZERO",
                dimension="autonomy_level",
                limit_value="NONE",
                requested_value=proposed_action,
                message="Agent has NONE autonomy level. All actions require manual intervention."
            ))
        elif policy.autonomy_level in (AgentAutonomyLevel.ASSISTED, AgentAutonomyLevel.SUPERVISED):
            requires_approval = True

        # 2. Prohibited actions
        if any(p in proposed_action.upper() for p in policy.boundary.prohibited_actions):
            violations.append(AutonomyViolation(
                violation_type="PROHIBITED_ACTION",
                dimension="action",
                limit_value=policy.boundary.prohibited_actions,
                requested_value=proposed_action,
                message=f"Action '{proposed_action}' is strictly prohibited under agent autonomy boundary."
            ))

        # 3. Target system
        if "*" not in policy.boundary.allowed_target_systems and target_system not in policy.boundary.allowed_target_systems:
            violations.append(AutonomyViolation(
                violation_type="UNAUTHORIZED_TARGET_SYSTEM",
                dimension="target_system",
                limit_value=policy.boundary.allowed_target_systems,
                requested_value=target_system,
                message=f"Target system '{target_system}' exceeds allowed target boundary."
            ))

        # 4. Financial limit
        if cost_dollars > policy.boundary.spending_limit_dollars:
            violations.append(AutonomyViolation(
                violation_type="SPENDING_LIMIT_EXCEEDED",
                dimension="spending_limit_dollars",
                limit_value=policy.boundary.spending_limit_dollars,
                requested_value=cost_dollars,
                message=f"Cost ${cost_dollars:.2f} exceeds spending limit of ${policy.boundary.spending_limit_dollars:.2f}."
            ))

        # 5. Step limit
        if estimated_steps > policy.boundary.max_steps:
            violations.append(AutonomyViolation(
                violation_type="STEP_LIMIT_EXCEEDED",
                dimension="max_steps",
                limit_value=policy.boundary.max_steps,
                requested_value=estimated_steps,
                message=f"Steps ({estimated_steps}) exceed maximum step boundary of {policy.boundary.max_steps}."
            ))

        is_allowed = len([v for v in violations if v.violation_type in ("PROHIBITED_ACTION", "UNAUTHORIZED_TARGET_SYSTEM", "SPENDING_LIMIT_EXCEEDED", "STEP_LIMIT_EXCEEDED")]) == 0
        return AutonomyEvaluation(
            is_allowed=is_allowed,
            autonomy_level=policy.autonomy_level,
            requires_approval=requires_approval or not is_allowed,
            violations=violations,
        )
