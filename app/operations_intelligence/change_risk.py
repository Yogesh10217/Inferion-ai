"""Change Risk Intelligence (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class ChangeRiskFactor(BaseModel):
    dimension: str  # AFFECTED_SERVICES, DEPENDENCY_IMPACT, HISTORICAL_INCIDENTS, SECURITY_RISK, RESILIENCE_RISK
    score: float
    description: str


class ChangeRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"chg_risk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    change_id: str
    overall_risk_score: float = 0.0
    risk_level: str = "MEDIUM"
    factors: List[ChangeRiskFactor] = Field(default_factory=list)
    is_high_risk: bool = False
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChangeRiskManager:
    """Evaluates multi-factor operational change risk."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ChangeRiskAssessment] = {}

    def evaluate_change_risk(
        self,
        tenant_id: str,
        change_id: str,
        affected_services_score: float = 20.0,
        dependency_impact_score: float = 20.0,
        security_risk_score: float = 20.0,
        is_emergency_change: bool = False,
    ) -> ChangeRiskAssessment:
        factors = [
            ChangeRiskFactor(dimension="AFFECTED_SERVICES", score=affected_services_score, description="Service blast radius"),
            ChangeRiskFactor(dimension="DEPENDENCY_IMPACT", score=dependency_impact_score, description="Downstream dependency impact"),
            ChangeRiskFactor(dimension="SECURITY_RISK", score=security_risk_score, description="Security policy posture"),
        ]
        base = sum(f.score for f in factors) / len(factors)
        if is_emergency_change:
            base = max(base, 85.0)

        composite = round(base, 2)
        if composite >= 80.0:
            level = "CRITICAL"
        elif composite >= 60.0:
            level = "HIGH"
        elif composite >= 40.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        asm = ChangeRiskAssessment(
            tenant_id=tenant_id,
            change_id=change_id,
            overall_risk_score=composite,
            risk_level=level,
            factors=factors,
            is_high_risk=composite >= 75.0,
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> ChangeRiskAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return asm
