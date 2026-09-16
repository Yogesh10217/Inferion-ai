"""Enterprise Model Trust Scoring Engine (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelTrustNotFoundException
from app.platform_contracts.trust import TrustAssessment

logger = logging.getLogger(__name__)


class ModelTrustDimension(str, Enum):
    QUALITY = "QUALITY"
    RELIABILITY = "RELIABILITY"
    SAFETY = "SAFETY"
    SECURITY = "SECURITY"
    GOVERNANCE = "GOVERNANCE"
    EXPLAINABILITY = "EXPLAINABILITY"


class ModelTrustFactor(BaseModel):
    dimension: ModelTrustDimension
    score: float  # 0.0 - 100.0
    weight: float = 1.0
    confidence: float = 1.0


class ModelTrustScore(BaseModel):
    overall_score: float  # 0.0 - 100.0
    trust_level: str  # VERY_HIGH, HIGH, MEDIUM, LOW, UNTRUSTED
    factors: List[ModelTrustFactor] = Field(default_factory=list)


class ModelTrustAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    trust_score: ModelTrustScore
    platform_trust_assessment: TrustAssessment
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelTrustEngine:
    """Computes comprehensive model trust scores and adapts to Platform TrustAssessment."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ModelTrustAssessment] = {}

    def calculate_trust(
        self,
        model_id: str,
        tenant_id: str,
        factors: List[ModelTrustFactor],
    ) -> ModelTrustAssessment:
        overall = sum(f.score * f.weight for f in factors) / max(sum(f.weight for f in factors), 1.0)

        level = "VERY_HIGH" if overall >= 90.0 else ("HIGH" if overall >= 75.0 else ("MEDIUM" if overall >= 60.0 else ("LOW" if overall >= 40.0 else "UNTRUSTED")))

        ts = ModelTrustScore(overall_score=overall, trust_level=level, factors=factors)

        from app.platform_contracts.trust import TrustBand
        from app.platform_contracts.trust import TrustDimension as PlatformTrustDimension
        band = TrustBand.HIGH_TRUST if overall >= 90.0 else (TrustBand.TRUSTED if overall >= 70.0 else TrustBand.UNTRUSTED)

        pta = TrustAssessment(
            subject_type="MODEL",
            subject_id=model_id,
            tenant_id=tenant_id,
            score=overall,
            band=band,
            dimensions=[PlatformTrustDimension(dimension_name=f.dimension.value, score=f.score, weight=f.weight) for f in factors],
        )

        assess = ModelTrustAssessment(
            assessment_id=f"trust-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            trust_score=ts,
            platform_trust_assessment=pta,
        )

        self._assessments[model_id] = assess
        logger.info(f"[MODEL TRUST ENGINE] Computed trust for model {model_id} (Tenant: {tenant_id}) Score: {overall:.1f} Level: {level}")
        return assess

    def get_trust_assessment(self, model_id: str, tenant_id: str) -> ModelTrustAssessment:
        assess = self._assessments.get(model_id)
        if not assess:
            raise ModelTrustNotFoundException(f"No trust assessment for model '{model_id}'.")
        if assess.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return assess
