"""
Governance Policy Evaluator Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Evaluates governance requirements for unified intelligence operations, enforcing approval gates,
raising HighRiskUnifiedActionRequiresApprovalException for unapproved high-risk actions.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.unified_intelligence.coordination import CoordinationPlan
from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    HighRiskUnifiedActionRequiresApprovalException,
    InvalidUnifiedIntelligenceInputException,
)
from app.unified_intelligence.recommendations import UnifiedRecommendation


class GovernanceEvaluationResult:
    """
    Result of a governance policy evaluation.
    """

    def __init__(
        self,
        evaluation_id: str,
        tenant_id: str,
        plan_id: Optional[str],
        recommendation_id: Optional[str],
        policy_status: str,  # APPROVED, REQUIRE_APPROVAL, REJECTED, VIOLATED
        reasons: List[str],
        risk_score: float,
        evaluated_at: Optional[datetime] = None,
    ):
        self.evaluation_id = evaluation_id
        self.tenant_id = tenant_id
        self.plan_id = plan_id
        self.recommendation_id = recommendation_id
        self.policy_status = policy_status
        self.reasons = reasons
        self.risk_score = min(max(risk_score, 0.0), 1.0)
        self.evaluated_at = evaluated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "tenant_id": self.tenant_id,
            "plan_id": self.plan_id,
            "recommendation_id": self.recommendation_id,
            "policy_status": self.policy_status,
            "reasons": self.reasons,
            "risk_score": round(self.risk_score, 4),
            "evaluated_at": self.evaluated_at.isoformat(),
        }


class GovernancePolicyEvaluatorEngine:
    """
    Enforces continuous enterprise governance policies over cross-domain intelligence decisions and delegation.
    """

    def __init__(self):
        pass

    def evaluate_recommendation(
        self, tenant_id: str, recommendation: UnifiedRecommendation, approved_by: Optional[str] = None
    ) -> GovernanceEvaluationResult:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if recommendation.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch in governance evaluation: expected {tenant_id}, got {recommendation.tenant_id}"
            )

        eval_id = f"gov-{uuid.uuid4().hex[:12]}"
        reasons = []

        # High risk action check
        is_high_risk = recommendation.priority in ["HIGH", "CRITICAL"] or recommendation.requires_human_approval

        if is_high_risk and not approved_by:
            reasons.append(
                f"Recommendation {recommendation.recommendation_id} is high risk and requires explicit human approval."
            )
            raise HighRiskUnifiedActionRequiresApprovalException(
                f"Governance policy requires human approval for action '{recommendation.title}' in tenant '{tenant_id}'."
            )

        status = "APPROVED" if approved_by or not is_high_risk else "REQUIRE_APPROVAL"
        if approved_by:
            reasons.append(f"Approved by human operator {approved_by}.")

        return GovernanceEvaluationResult(
            evaluation_id=eval_id,
            tenant_id=tenant_id,
            plan_id=None,
            recommendation_id=recommendation.recommendation_id,
            policy_status=status,
            reasons=reasons,
            risk_score=0.3 if approved_by else 0.5,
        )

    def evaluate_coordination_plan(
        self, tenant_id: str, plan: CoordinationPlan, approved_by: Optional[str] = None
    ) -> GovernanceEvaluationResult:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if plan.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch in plan governance evaluation: expected {tenant_id}, got {plan.tenant_id}"
            )

        requires_appr = any(step.requires_approval for step in plan.steps)
        eval_id = f"gov-{uuid.uuid4().hex[:12]}"
        reasons = []

        if requires_appr and not approved_by:
            reasons.append(f"Coordination plan {plan.plan_id} contains steps requiring explicit human approval.")
            raise HighRiskUnifiedActionRequiresApprovalException(
                f"High-risk coordination plan '{plan.title}' requires human approval before execution."
            )

        return GovernanceEvaluationResult(
            evaluation_id=eval_id,
            tenant_id=tenant_id,
            plan_id=plan.plan_id,
            recommendation_id=plan.recommendation_id,
            policy_status="APPROVED" if approved_by or not requires_appr else "REQUIRE_APPROVAL",
            reasons=["Plan evaluated successfully."],
            risk_score=0.2 if approved_by else 0.4,
        )
