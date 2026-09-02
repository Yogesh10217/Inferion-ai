"""Resource Efficiency Intelligence (Phase 5.42)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class EfficiencyDimension(str, Enum):
    COST = "COST"
    PERFORMANCE = "PERFORMANCE"
    UTILIZATION = "UTILIZATION"
    MODEL_EFFICIENCY = "MODEL_EFFICIENCY"


class EfficiencyRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"eff_rec_{uuid.uuid4().hex[:8]}")
    title: str
    action: str


class EfficiencyScore(BaseModel):
    dimension: EfficiencyDimension
    score: float  # 0 to 100
    description: str


class EfficiencyAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"eff_asm_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_resource_id: str
    overall_efficiency_score: float = 85.0
    scores: List[EfficiencyScore] = Field(default_factory=list)
    recommendations: List[EfficiencyRecommendation] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResourceEfficiencyManager:
    """Evaluates multi-dimensional resource and AI model efficiency."""

    def __init__(self) -> None:
        self._assessments: Dict[str, EfficiencyAssessment] = {}

    def evaluate_efficiency(
        self,
        tenant_id: str,
        target_resource_id: str,
        cost_score: float = 80.0,
        utilization_score: float = 75.0,
        model_efficiency_score: float = 90.0,
    ) -> EfficiencyAssessment:
        scores = [
            EfficiencyScore(dimension=EfficiencyDimension.COST, score=cost_score, description="Cost efficiency score"),
            EfficiencyScore(dimension=EfficiencyDimension.UTILIZATION, score=utilization_score, description="Capacity utilization score"),
            EfficiencyScore(dimension=EfficiencyDimension.MODEL_EFFICIENCY, score=model_efficiency_score, description="Model efficiency score"),
        ]
        overall = round(sum(s.score for s in scores) / len(scores), 2)
        recs: List[EfficiencyRecommendation] = []
        if model_efficiency_score < 70.0:
            recs.append(EfficiencyRecommendation(title="Model Rightsizing", action="Switch to quantized or smaller parameters model."))

        asm = EfficiencyAssessment(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            overall_efficiency_score=overall,
            scores=scores,
            recommendations=recs,
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> EfficiencyAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return asm
