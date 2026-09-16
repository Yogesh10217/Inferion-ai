"""Control Assurance Governance Engine Subsystem (Phase 5.38)."""

import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import GovernanceDecision, UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.platform_contracts.tenant import TenantAccessGuard


class ControlGovernanceRequirement(BaseModel):
    requirement_code: str
    is_mandatory: bool = True


class ControlGovernanceContext(BaseModel):
    tenant_id: str
    control_id: str
    action_type: str
    is_high_risk: bool = False


class ControlGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"gdec_{uuid.uuid4().hex[:12]}")
    decision: GovernanceDecision = GovernanceDecision.ALLOW
    reasons: List[str] = Field(default_factory=list)
    evaluator: str = "ControlGovernanceEngine"


class ControlGovernanceEngine:
    """Evaluates governance decisions for control operations."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.policy_evaluator = UnifiedPolicyEvaluator()
        self.risk_manager = RiskManager()
        self.approval_engine = ApprovalEngine()

    def evaluate_action_governance(
        self,
        tenant_id: str,
        action_type: str,
        control_id: str,
        is_high_risk: bool = False,
    ) -> ControlGovernanceDecision:
        if is_high_risk:
            decision = GovernanceDecision.REQUIRE_APPROVAL
            reasons = [f"Action '{action_type}' on control '{control_id}' is high-risk and requires approval."]
        else:
            decision = GovernanceDecision.ALLOW
            reasons = ["Action allowed under current control assurance policy."]

        return ControlGovernanceDecision(
            decision=decision,
            reasons=reasons,
        )
