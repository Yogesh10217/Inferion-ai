"""Financial Risk Intelligence (Phase 5.42)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException
from app.governance_platform.risk import RiskManager, RiskLevel


class FinOpsRiskDimension(str, Enum):
    BUDGET_RISK = "BUDGET_RISK"
    FORECAST_RISK = "FORECAST_RISK"
    OPTIMIZATION_RISK = "OPTIMIZATION_RISK"
    OPERATIONAL_RISK = "OPERATIONAL_RISK"
    COMMITMENT_RISK = "COMMITMENT_RISK"


class FinOpsRiskFactor(BaseModel):
    dimension: FinOpsRiskDimension
    score: float
    description: str


class FinOpsRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"risk_prof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_entity: str
    overall_risk_score: float = 0.0
    risk_level: str = "LOW"
    factors: List[FinOpsRiskFactor] = Field(default_factory=list)


class FinOpsRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"fin_risk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    profile: FinOpsRiskProfile
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsRiskManager:
    """Evaluates multi-dimensional financial risk composing with platform RiskManager."""

    def __init__(self) -> None:
        self.risk_manager = RiskManager()
        self._assessments: Dict[str, FinOpsRiskAssessment] = {}

    def evaluate_risk(
        self,
        tenant_id: str,
        target_entity: str,
        budget_risk_score: float = 10.0,
        forecast_risk_score: float = 10.0,
        commitment_risk_score: float = 10.0,
    ) -> FinOpsRiskAssessment:
        factors = [
            FinOpsRiskFactor(dimension=FinOpsRiskDimension.BUDGET_RISK, score=budget_risk_score, description="Budget utilization risk"),
            FinOpsRiskFactor(dimension=FinOpsRiskDimension.FORECAST_RISK, score=forecast_risk_score, description="Spending forecast variance risk"),
            FinOpsRiskFactor(dimension=FinOpsRiskDimension.COMMITMENT_RISK, score=commitment_risk_score, description="Long-term commitment lock-in risk"),
        ]
        composite = round(sum(f.score for f in factors) / len(factors), 2)

        if composite >= 80.0:
            level = "CRITICAL"
        elif composite >= 60.0:
            level = "HIGH"
        elif composite >= 40.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        prof = FinOpsRiskProfile(
            tenant_id=tenant_id,
            target_entity=target_entity,
            overall_risk_score=composite,
            risk_level=level,
            factors=factors,
        )
        asm = FinOpsRiskAssessment(tenant_id=tenant_id, profile=prof)
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> FinOpsRiskAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return asm
