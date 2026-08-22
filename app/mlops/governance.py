"""AI Release Governance & Policy Enforcement Subsystem."""

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.mlops.evaluation import EvaluationResult
from app.mlops.exceptions import GovernanceViolationException

logger = logging.getLogger(__name__)


class DeploymentPolicy(BaseModel):
    policy_id: str = "default_policy"
    tenant_id: str = "global"
    min_evaluation_score: float = 90.0
    min_safety_score: float = 95.0
    max_hallucination_rate: float = 0.05
    require_approval_for_production: bool = True


class PromotionDecision(BaseModel):
    approved: bool
    requires_approval: bool = False
    reasons: List[str] = Field(default_factory=list)


class MLOpsGovernanceEngine:
    """Evaluates release policies, security thresholds, and approval requirements for AI asset promotion."""

    def __init__(self) -> None:
        self._policies: Dict[str, DeploymentPolicy] = {
            "global": DeploymentPolicy(),
        }

    def evaluate_promotion(
        self,
        tenant_id: str,
        target_environment: str,
        evaluation_result: Optional[EvaluationResult] = None,
    ) -> PromotionDecision:
        pol = self._policies.get(tenant_id, self._policies["global"])
        reasons = []

        if evaluation_result:
            if evaluation_result.overall_score < pol.min_evaluation_score:
                reasons.append(f"Evaluation score {evaluation_result.overall_score:.1f}% below minimum {pol.min_evaluation_score:.1f}%")
            if evaluation_result.safety_score < pol.min_safety_score:
                reasons.append(f"Safety score {evaluation_result.safety_score:.1f}% below minimum {pol.min_safety_score:.1f}%")
            if evaluation_result.hallucination_rate > pol.max_hallucination_rate:
                reasons.append(f"Hallucination rate {evaluation_result.hallucination_rate:.3f} exceeds maximum {pol.max_hallucination_rate:.3f}")

        requires_appr = (target_environment.upper() == "PRODUCTION") and pol.require_approval_for_production
        approved = len(reasons) == 0

        logger.info(f"[MLOPS GOVERNANCE] Evaluated promotion to '{target_environment}' for tenant '{tenant_id}': Approved = {approved}, Requires Approval = {requires_appr}")
        return PromotionDecision(approved=approved, requires_approval=requires_appr, reasons=reasons)
