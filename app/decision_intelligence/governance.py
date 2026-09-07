"""Decision Governance Orchestration Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine
from app.orchestration.human_tasks import HumanTaskManager


class DecisionGovernanceStatus(str, Enum):
    ALLOW = "ALLOW"
    APPROVED = "APPROVED"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ESCALATE = "ESCALATE"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class DecisionGovernanceDecision(BaseModel):
    governance_id: str = Field(default_factory=lambda: f"decgov_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    decision_id: str
    status: DecisionGovernanceStatus = DecisionGovernanceStatus.APPROVED
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    reason: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionGovernanceEngine:
    """Evaluates decision policies, risk thresholds, and human approval triggers."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
        human_task_manager: Optional[HumanTaskManager] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()
        self.human_task_manager = human_task_manager or HumanTaskManager()

    def evaluate_decision_governance(
        self,
        tenant_id: str,
        decision_id: str,
        risk_score: float,
        trust_score: float,
        amount_usd: float = 0.0,
        requested_by: str = "decision_lead",
    ) -> DecisionGovernanceDecision:
        requires_approval = (risk_score >= 50.0) or (trust_score < 70.0) or (amount_usd > 100000.0)
        app_req_id = None

        if requires_approval:
            gov_status = DecisionGovernanceStatus.REQUIRE_APPROVAL
            reason = f"Decision '{decision_id}' carries Risk {risk_score:.1f}, Trust {trust_score:.1f}, or exceeds financial threshold (${amount_usd:,.2f}). Human approval required."
            app_req = self.approval_engine.request_approval(
                execution_id=decision_id,
                action_type="ENTERPRISE_DECISION_APPROVAL",
                requester=requested_by,
                tenant_id=tenant_id,
                payload={"decision_id": decision_id, "amount_usd": amount_usd, "risk_score": risk_score},
            )
            app_req_id = app_req.request_id
        else:
            gov_status = DecisionGovernanceStatus.APPROVED
            reason = "Decision approved within autonomous thresholds."

        return DecisionGovernanceDecision(
            tenant_id=tenant_id,
            decision_id=decision_id,
            status=gov_status,
            requires_approval=requires_approval,
            approval_request_id=app_req_id,
            reason=reason,
        )
