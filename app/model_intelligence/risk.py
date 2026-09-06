"""Multi-Dimensional Model Risk Intelligence (Phase 5.44)."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import ModelRiskNotFoundException, CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class ModelRiskDimension(str, Enum):
    PERFORMANCE = "PERFORMANCE"
    RELIABILITY = "RELIABILITY"
    SAFETY = "SAFETY"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    FINANCIAL = "FINANCIAL"
    OPERATIONAL = "OPERATIONAL"


class ModelRiskFactor(BaseModel):
    dimension: ModelRiskDimension
    risk_score: float  # 0.0 - 1.0 (1.0 = extreme risk)
    weight: float = 1.0
    description: str


class ModelRiskProfile(BaseModel):
    profile_id: str
    model_id: str
    tenant_id: str
    overall_risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: List[ModelRiskFactor] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRiskAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    profile: ModelRiskProfile
    acceptable: bool = True
    mitigation_required: bool = False
    recommendations: List[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRiskManager:
    """Manages multi-dimensional model risk intelligence adapting RiskManager."""

    def __init__(self) -> None:
        self._risk_profiles: Dict[str, ModelRiskProfile] = {}

    def assess_risk(
        self,
        model_id: str,
        tenant_id: str,
        factors: List[ModelRiskFactor],
    ) -> ModelRiskAssessment:
        overall = sum(f.risk_score * f.weight for f in factors) / max(sum(f.weight for f in factors), 1.0)

        risk_level = "LOW" if overall < 0.25 else ("MEDIUM" if overall < 0.5 else ("HIGH" if overall < 0.75 else "CRITICAL"))
        acceptable = overall < 0.5
        mitigation = overall >= 0.5

        recs = []
        if mitigation:
            recs.append("Trigger risk mitigation plan")
            recs.append("Conduct comprehensive safety and security review")

        prof_id = f"rprof-{uuid.uuid4().hex[:8]}"
        profile = ModelRiskProfile(
            profile_id=prof_id,
            model_id=model_id,
            tenant_id=tenant_id,
            overall_risk_score=overall,
            risk_level=risk_level,
            factors=factors,
        )

        self._risk_profiles[model_id] = profile

        assessment = ModelRiskAssessment(
            assessment_id=f"rassess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            profile=profile,
            acceptable=acceptable,
            mitigation_required=mitigation,
            recommendations=recs,
        )

        logger.info(f"[MODEL RISK] Assessed {model_id} (Tenant: {tenant_id}) Score: {overall:.2f} Level: {risk_level}")
        return assessment

    def get_risk_profile(self, model_id: str, tenant_id: str) -> ModelRiskProfile:
        prof = self._risk_profiles.get(model_id)
        if not prof:
            raise ModelRiskNotFoundException(f"No risk profile found for model '{model_id}'.")
        if prof.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return prof
