"""Optimization Governance & Risk Approval Policy Subsystem."""

import logging
from typing import Optional

from pydantic import BaseModel

from app.approvals.approval_engine import ApprovalEngine
from app.finops.optimization import OptimizationRecommendation, OptimizationRiskLevel

logger = logging.getLogger(__name__)


class OptimizationDecision(BaseModel):
    recommendation_id: str
    permitted: bool
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    reason: str = ""


class FinOpsGovernanceEngine:
    """Evaluates optimization risk levels (LOW, MEDIUM, HIGH, CRITICAL) and enforces ApprovalEngine gating for HIGH/CRITICAL actions."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_optimization(self, recommendation: OptimizationRecommendation) -> OptimizationDecision:
        risk = recommendation.risk_level

        if risk == OptimizationRiskLevel.LOW:
            logger.info(f"[FINOPS GOVERNANCE] LOW risk optimization '{recommendation.recommendation_id}' automatically permitted")
            return OptimizationDecision(recommendation_id=recommendation.recommendation_id, permitted=True, reason="LOW risk automatically permitted by policy")

        elif risk == OptimizationRiskLevel.MEDIUM:
            logger.info(f"[FINOPS GOVERNANCE] MEDIUM risk optimization '{recommendation.recommendation_id}' permitted under policy")
            return OptimizationDecision(recommendation_id=recommendation.recommendation_id, permitted=True, reason="MEDIUM risk permitted under active policy")

        else:
            # HIGH and CRITICAL risk optimizations REQUIRE ApprovalEngine approval!
            req_id = f"opt_appr_{recommendation.recommendation_id[:8]}"
            logger.warning(f"[FINOPS GOVERNANCE] {risk.value} risk optimization '{recommendation.recommendation_id}' REQUIRES APPROVAL (Request ID: {req_id})")
            return OptimizationDecision(
                recommendation_id=recommendation.recommendation_id,
                permitted=False,
                requires_approval=True,
                approval_request_id=req_id,
                reason=f"{risk.value} risk requires explicit administrator approval",
            )
