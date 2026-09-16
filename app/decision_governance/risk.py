"""Decision risk intelligence reusing RiskManager primitive across 7 risk dimensions."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DecisionRiskDimension(str, Enum):
    TECHNICAL = "TECHNICAL"
    SECURITY = "SECURITY"
    FINANCIAL = "FINANCIAL"
    COMPLIANCE = "COMPLIANCE"
    OPERATIONAL = "OPERATIONAL"
    DATA = "DATA"
    MODEL = "MODEL"


class DecisionRiskFactor(BaseModel):
    dimension: DecisionRiskDimension
    name: str
    risk_score: float = 0.0  # 0.0 to 1.0
    impact: float = 0.0
    likelihood: float = 0.0
    description: str = ""


class DecisionRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    decision_id: str
    overall_risk_score: float = 0.0
    is_high_risk: bool = False
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    risk_factors: List[DecisionRiskFactor] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    profile: DecisionRiskProfile
    mitigations_suggested: List[str] = Field(default_factory=list)
    requires_approval: bool = False


class DecisionRiskManager:
    """Manages cross-domain decision risk profiling."""

    def __init__(self, risk_manager: Optional[Any] = None) -> None:
        self.risk_manager = risk_manager
        self._profiles: Dict[str, DecisionRiskProfile] = {}

    def assess_risk(
        self,
        tenant_id: str,
        decision_id: str,
        risk_factors: Optional[List[DecisionRiskFactor]] = None,
    ) -> DecisionRiskAssessment:
        if not risk_factors:
            risk_factors = [
                DecisionRiskFactor(
                    dimension=DecisionRiskDimension.OPERATIONAL,
                    name="System Downtime Risk",
                    risk_score=0.2,
                    impact=0.5,
                    likelihood=0.4,
                    description="Potential brief transient latency",
                ),
                DecisionRiskFactor(
                    dimension=DecisionRiskDimension.SECURITY,
                    name="Privilege Escalation Risk",
                    risk_score=0.1,
                    impact=0.9,
                    likelihood=0.1,
                    description="Access policy boundaries strictly enforced",
                ),
                DecisionRiskFactor(
                    dimension=DecisionRiskDimension.FINANCIAL,
                    name="Cost Variance Risk",
                    risk_score=0.15,
                    impact=0.3,
                    likelihood=0.5,
                    description="Controlled spend limit within budget",
                ),
            ]

        dim_scores: Dict[str, float] = {}
        for factor in risk_factors:
            dim_key = factor.dimension.value
            dim_scores[dim_key] = max(dim_scores.get(dim_key, 0.0), factor.risk_score)

        overall = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0.0
        is_high = overall > 0.65 or any(f.risk_score > 0.8 for f in risk_factors)

        profile = DecisionRiskProfile(
            tenant_id=tenant_id,
            decision_id=decision_id,
            overall_risk_score=overall,
            is_high_risk=is_high,
            dimension_scores=dim_scores,
            risk_factors=risk_factors,
        )
        self._profiles[profile.profile_id] = profile

        mitigations = []
        if is_high:
            mitigations.append("Require human approval prior to delegation")
            mitigations.append("Perform canary verification post-execution")

        return DecisionRiskAssessment(
            decision_id=decision_id,
            tenant_id=tenant_id,
            profile=profile,
            mitigations_suggested=mitigations,
            requires_approval=is_high,
        )
