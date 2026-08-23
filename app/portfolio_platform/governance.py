"""Portfolio Governance Engine Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine


class PortfolioGovernanceDecisionType(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class InvestmentRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"portrisk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    risk_score: float = 20.0
    risk_level: str = "LOW"
    risk_factors: List[str] = Field(default_factory=list)


class PortfolioGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"portdec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    decision: PortfolioGovernanceDecisionType
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    reason: str
    risk_assessment: InvestmentRiskAssessment
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioGovernanceEngine:
    """Evaluates portfolio investment governance, policy rules, and human approval triggers."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_investment_governance(
        self,
        tenant_id: str,
        initiative_id: str,
        amount_usd: float,
        risk_level: str = "HIGH",
        architecture_trust: float = 90.0,
        compliance_score: float = 90.0,
        requested_by: str = "program_lead",
    ) -> PortfolioGovernanceDecision:
        requires_approval = (
            risk_level in ("HIGH", "CRITICAL")
            or amount_usd > 100000.0
            or architecture_trust < 70.0
            or compliance_score < 70.0
        )
        approval_req_id = None

        if requires_approval:
            decision_type = PortfolioGovernanceDecisionType.REQUIRE_APPROVAL
            reason = f"Initiative '{initiative_id}' carries {risk_level} risk or exceeds threshold, requiring explicit approval."
            app_req = self.approval_engine.request_approval(
                execution_id=initiative_id,
                action_type="PORTFOLIO_INVESTMENT_APPROVAL",
                requester=requested_by,
                tenant_id=tenant_id,
                payload={"initiative_id": initiative_id, "amount_usd": amount_usd, "risk_level": risk_level},
            )
            approval_req_id = app_req.request_id
        else:
            decision_type = PortfolioGovernanceDecisionType.ALLOW
            reason = "Investment approved within autonomous thresholds."

        risk_assessment = InvestmentRiskAssessment(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            risk_score=85.0 if requires_approval else 20.0,
            risk_level=risk_level,
            risk_factors=[f"Initiative: {initiative_id}", f"Amount: ${amount_usd:,.2f}", f"Risk: {risk_level}"],
        )

        return PortfolioGovernanceDecision(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            decision=decision_type,
            requires_approval=requires_approval,
            approval_request_id=approval_req_id,
            reason=reason,
            risk_assessment=risk_assessment,
        )
