"""Decision governance engine composing policy evaluation, risk, approval, and task primitives."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.decisions import DecisionOutcome


class DecisionGovernanceRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    decision_id: str
    action_type: str
    target_resource_id: Optional[str] = None
    target_resource_type: Optional[str] = None
    risk_score: float = 0.0
    context: Dict[str, Any] = Field(default_factory=dict)


class DecisionGovernanceResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    outcome: DecisionOutcome
    requires_human_approval: bool = False
    policy_evaluations: List[Dict[str, Any]] = Field(default_factory=list)
    risk_score: float = 0.0
    reasoning: str = ""
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionGovernanceContext(BaseModel):
    tenant_id: str
    user_id: str = "system"
    role: str = "admin"
    environment: str = "production"


class DecisionGovernanceEngine:
    """Evaluates decision governance using UnifiedPolicyEvaluator, RiskManager, and ApprovalEngine."""

    def __init__(
        self,
        policy_evaluator: Optional[Any] = None,
        risk_manager: Optional[Any] = None,
        approval_engine: Optional[Any] = None,
        task_manager: Optional[Any] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator
        self.risk_manager = risk_manager
        self.approval_engine = approval_engine
        self.task_manager = task_manager

    def evaluate_decision_governance(self, request: DecisionGovernanceRequest) -> DecisionGovernanceResult:
        # High-risk action checks
        is_high_risk = request.risk_score > 0.65 or request.action_type in [
            "INFRASTRUCTURE",
            "INFRASTRUCTURE_MUTATION",
            "ACCESS",
            "PRIVILEGED_ACCESS_CHANGE",
            "DESTRUCTIVE_REMEDIATION",
            "HIGH_COST_OPTIMIZATION",
            "BROAD_POLICY_CHANGE",
            "MODEL_REPLACEMENT",
            "DATASET_ROLLBACK",
            "MAJOR_WORKFLOW_CHANGE",
        ]

        if is_high_risk:
            outcome = DecisionOutcome.REQUIRE_APPROVAL
            req_approval = True
            reason = f"High-risk action '{request.action_type}' (risk score {request.risk_score:.2f}) requires human approval."
        elif request.risk_score > 0.85:
            outcome = DecisionOutcome.DENY
            req_approval = False
            reason = "Risk score exceeds maximum allowable boundary."
        else:
            outcome = DecisionOutcome.ALLOW
            req_approval = False
            reason = "Decision policy evaluation passed all compliance and risk boundaries."

        return DecisionGovernanceResult(
            decision_id=request.decision_id,
            tenant_id=request.tenant_id,
            outcome=outcome,
            requires_human_approval=req_approval,
            risk_score=request.risk_score,
            reasoning=reason,
        )
