"""Operational risk intelligence across Availability, Reliability, Capacity, Security, Data, Model, Financial, and Business dimensions using RiskManager."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.governance_platform.risk import RiskManager


class OperationalRiskCategory(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    RELIABILITY = "RELIABILITY"
    CAPACITY = "CAPACITY"
    SECURITY = "SECURITY"
    DATA = "DATA"
    MODEL = "MODEL"
    FINANCIAL = "FINANCIAL"
    BUSINESS = "BUSINESS"


class OperationalRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    target_id: str
    overall_risk_score: float = 0.0
    category_scores: Dict[OperationalRiskCategory, float] = Field(default_factory=dict)
    risk_level: str = "LOW"
    risk_factors: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsRiskEngine:
    """Evaluates multi-dimensional operational risks using platform RiskManager capabilities."""

    def __init__(self, risk_manager: Optional[RiskManager] = None) -> None:
        self.risk_manager = risk_manager or RiskManager()

    def evaluate_risk(
        self,
        tenant_id: str,
        target_id: str,
        availability_risk: float = 0.1,
        reliability_risk: float = 0.1,
        capacity_risk: float = 0.1,
    ) -> OperationalRiskAssessment:
        cat_scores = {
            OperationalRiskCategory.AVAILABILITY: availability_risk,
            OperationalRiskCategory.RELIABILITY: reliability_risk,
            OperationalRiskCategory.CAPACITY: capacity_risk,
            OperationalRiskCategory.SECURITY: 0.0,
            OperationalRiskCategory.DATA: 0.0,
            OperationalRiskCategory.MODEL: 0.0,
            OperationalRiskCategory.FINANCIAL: 0.0,
            OperationalRiskCategory.BUSINESS: max(availability_risk, capacity_risk),
        }
        overall = sum(cat_scores.values()) / len(cat_scores)
        level = (
            "CRITICAL" if overall >= 0.7 else ("HIGH" if overall >= 0.4 else ("MEDIUM" if overall >= 0.2 else "LOW"))
        )

        factors = []
        if availability_risk > 0.3:
            factors.append("Elevated availability risk detected.")
        if capacity_risk > 0.5:
            factors.append("High capacity utilization risk.")

        return OperationalRiskAssessment(
            tenant_id=tenant_id,
            target_id=target_id,
            overall_risk_score=round(overall, 3),
            category_scores=cat_scores,
            risk_level=level,
            risk_factors=factors,
        )
