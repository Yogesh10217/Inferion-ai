"""Decision priority evaluation intelligence across business impact, urgency, risk, and cost."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.decisions import DecisionPriority


class PriorityFactor(BaseModel):
    name: str  # business_impact, urgency, risk, cost, reliability, compliance, trust
    weight: float = 1.0
    score: float = 0.0
    justification: str = ""


class PriorityScore(BaseModel):
    overall_score: float = 0.0
    calculated_priority: DecisionPriority = DecisionPriority.MEDIUM


class PriorityRecommendation(BaseModel):
    recommended_priority: DecisionPriority
    rationale: str
    target_sla_minutes: int = 60


class DecisionPriorityAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    factors: List[PriorityFactor] = Field(default_factory=list)
    score: PriorityScore = Field(default_factory=PriorityScore)
    recommendation: PriorityRecommendation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionPriorityManager:
    """Evaluates decision priority based on cross-domain factors."""

    def __init__(self) -> None:
        self._assessments: Dict[str, DecisionPriorityAssessment] = {}

    def evaluate_priority(
        self,
        tenant_id: str,
        decision_id: str,
        factors: Optional[List[PriorityFactor]] = None,
    ) -> DecisionPriorityAssessment:
        if not factors:
            factors = [
                PriorityFactor(name="business_impact", weight=0.25, score=0.8, justification="High business value"),
                PriorityFactor(name="urgency", weight=0.25, score=0.9, justification="SLA deadline approaching"),
                PriorityFactor(name="risk", weight=0.20, score=0.5, justification="Moderate operational risk"),
                PriorityFactor(name="compliance", weight=0.15, score=0.95, justification="Regulated workload"),
                PriorityFactor(name="cost", weight=0.15, score=0.4, justification="Low cost delta"),
            ]

        total_weight = sum(f.weight for f in factors)
        weighted_sum = sum(f.weight * f.score for f in factors)
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.5

        if final_score >= 0.85:
            p = DecisionPriority.CRITICAL
            sla = 15
        elif final_score >= 0.70:
            p = DecisionPriority.HIGH
            sla = 30
        elif final_score >= 0.40:
            p = DecisionPriority.MEDIUM
            sla = 120
        else:
            p = DecisionPriority.LOW
            sla = 480

        assessment = DecisionPriorityAssessment(
            tenant_id=tenant_id,
            decision_id=decision_id,
            factors=factors,
            score=PriorityScore(overall_score=final_score, calculated_priority=p),
            recommendation=PriorityRecommendation(
                recommended_priority=p,
                rationale=f"Calculated priority score {final_score:.2f} maps to {p.value}",
                target_sla_minutes=sla,
            ),
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
