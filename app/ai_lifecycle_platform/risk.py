"""Lifecycle Risk Composition Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from app.governance_platform.risk import RiskAssessment, RiskCategory, RiskFactor, RiskManager, RiskSeverity


class LifecycleRiskDimension(BaseModel):
    name: str
    risk_level: RiskSeverity = RiskSeverity.MEDIUM
    score: float = 50.0


class LifecycleRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"lrp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    overall_risk_level: RiskSeverity = RiskSeverity.HIGH
    dimensions: List[LifecycleRiskDimension] = Field(default_factory=list)


class LifecycleRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"lra_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    contract_risk: RiskAssessment
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LifecycleRiskManager:
    """Composes lifecycle risk evaluation with enterprise RiskManager."""

    def __init__(self, enterprise_risk_manager: Optional[RiskManager] = None) -> None:
        self.enterprise_risk_manager = enterprise_risk_manager or RiskManager()

    def assess_lifecycle_risk(
        self,
        tenant_id: str,
        asset_id: str,
        eval_score: float = 0.90,
    ) -> LifecycleRiskAssessment:
        impact = float(round((1.0 - eval_score) * 100.0, 2))
        factors = [RiskFactor(name="evaluation_score", weight=1.0, impact_score=impact)]
        base_assessment = self.enterprise_risk_manager.calculate_risk(
            target_resource_id=asset_id,
            factors=factors,
            category=RiskCategory.MODEL,
            tenant_id=tenant_id,
        )
        return LifecycleRiskAssessment(
            tenant_id=tenant_id,
            asset_id=asset_id,
            contract_risk=base_assessment,
        )
