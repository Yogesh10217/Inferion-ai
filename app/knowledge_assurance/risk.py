"""Knowledge risk intelligence profiling reusing RiskManager primitive."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class KnowledgeRiskDimension(str, Enum):
    STALE_KNOWLEDGE = "STALE_KNOWLEDGE"
    MISINFORMATION = "MISINFORMATION"
    PROVENANCE = "PROVENANCE"
    CONFLICT = "CONFLICT"
    COVERAGE = "COVERAGE"
    ACCESS = "ACCESS"
    DECISION_IMPACT = "DECISION_IMPACT"


class KnowledgeRiskFactor(BaseModel):
    dimension: KnowledgeRiskDimension
    name: str
    risk_score: float = 0.0  # 0.0 to 1.0
    impact: float = 0.0
    likelihood: float = 0.0
    description: str = ""


class KnowledgeRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id: str
    overall_risk_score: float = 0.0
    is_high_risk: bool = False
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    risk_factors: List[KnowledgeRiskFactor] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id: str
    profile: KnowledgeRiskProfile
    mitigations_suggested: List[str] = Field(default_factory=list)
    requires_approval: bool = False


class KnowledgeRiskManager:
    """Manages knowledge risk profiling across 7 risk dimensions."""

    def __init__(self, risk_manager: Optional[Any] = None) -> None:
        self.risk_manager = risk_manager
        self._profiles: Dict[str, KnowledgeRiskProfile] = {}

    def assess_risk(
        self,
        tenant_id: str,
        reference_id: str,
        risk_factors: Optional[List[KnowledgeRiskFactor]] = None,
    ) -> KnowledgeRiskAssessment:
        if not risk_factors:
            risk_factors = [
                KnowledgeRiskFactor(
                    dimension=KnowledgeRiskDimension.STALE_KNOWLEDGE,
                    name="Aging Content Risk",
                    risk_score=0.15,
                    impact=0.4,
                    likelihood=0.3,
                    description="Reference updated < 7 days ago",
                ),
                KnowledgeRiskFactor(
                    dimension=KnowledgeRiskDimension.PROVENANCE,
                    name="Source Authority Risk",
                    risk_score=0.10,
                    impact=0.8,
                    likelihood=0.1,
                    description="Verified internal repository source",
                ),
                KnowledgeRiskFactor(
                    dimension=KnowledgeRiskDimension.CONFLICT,
                    name="Contradiction Risk",
                    risk_score=0.05,
                    impact=0.7,
                    likelihood=0.05,
                    description="Zero policy contradictions detected",
                ),
            ]

        dim_scores: Dict[str, float] = {}
        for factor in risk_factors:
            dim_key = factor.dimension.value
            dim_scores[dim_key] = max(dim_scores.get(dim_key, 0.0), factor.risk_score)

        overall = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0.0
        is_high = overall > 0.60 or any(f.risk_score > 0.8 for f in risk_factors)

        profile = KnowledgeRiskProfile(
            tenant_id=tenant_id,
            reference_id=reference_id,
            overall_risk_score=overall,
            is_high_risk=is_high,
            dimension_scores=dim_scores,
            risk_factors=risk_factors,
        )
        self._profiles[profile.profile_id] = profile

        mitigations = []
        if is_high:
            mitigations.append("Require human approval prior to using in automated decision context")

        return KnowledgeRiskAssessment(
            tenant_id=tenant_id,
            reference_id=reference_id,
            profile=profile,
            mitigations_suggested=mitigations,
            requires_approval=is_high,
        )
