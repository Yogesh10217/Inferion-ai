"""Model Reliability Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class ReliabilityDimension(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    ERROR_RESILIENCE = "ERROR_RESILIENCE"
    TIMEOUT_RESILIENCE = "TIMEOUT_RESILIENCE"
    RATE_LIMIT_RESILIENCE = "RATE_LIMIT_RESILIENCE"
    FALLBACK_SUCCESS = "FALLBACK_SUCCESS"


class ReliabilityScore(BaseModel):
    dimension: ReliabilityDimension
    score: float  # 0.0 - 1.0
    weight: float = 1.0


class ModelFailurePattern(BaseModel):
    pattern_id: str
    failure_type: str
    occurrences: int
    impact_level: str = "MEDIUM"
    description: str


class ModelReliabilityAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    overall_reliability_score: float
    scores: List[ReliabilityScore]
    failure_patterns: List[ModelFailurePattern] = Field(default_factory=list)
    resilient: bool = True
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelReliabilityManager:
    """Manages model reliability intelligence adapting existing platform resilience primitives."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ModelReliabilityAssessment] = {}

    def assess_reliability(
        self,
        model_id: str,
        tenant_id: str,
        scores: List[ReliabilityScore],
        failure_patterns: Optional[List[ModelFailurePattern]] = None,
    ) -> ModelReliabilityAssessment:
        overall = sum(s.score * s.weight for s in scores) / max(sum(s.weight for s in scores), 1.0)
        resilient = overall >= 0.9 and not any(p.impact_level == "CRITICAL" for p in (failure_patterns or []))

        assessment = ModelReliabilityAssessment(
            assessment_id=f"rel-assess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            overall_reliability_score=overall,
            scores=scores,
            failure_patterns=failure_patterns or [],
            resilient=resilient,
        )

        self._assessments[assessment.assessment_id] = assessment
        logger.info(f"[MODEL RELIABILITY] Assessed {model_id} (Tenant: {tenant_id}) Score: {overall:.2f} Resilient: {resilient}")
        return assessment

    def get_latest_assessment(self, model_id: str, tenant_id: str) -> Optional[ModelReliabilityAssessment]:
        matches = [a for a in self._assessments.values() if a.model_id == model_id]
        if not matches:
            return None
        latest = matches[-1]
        if latest.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return latest
