"""Access Risk Intelligence (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException, AccessRiskThresholdExceededException


class AccessRiskDimension(str, Enum):
    PRIVILEGE_LEVEL = "PRIVILEGE_LEVEL"
    RESOURCE_SENSITIVITY = "RESOURCE_SENSITIVITY"
    IDENTITY_TRUST = "IDENTITY_TRUST"
    EXPOSURE = "EXPOSURE"
    ABNORMAL_USAGE = "ABNORMAL_USAGE"
    TOXIC_COMBINATION = "TOXIC_COMBINATION"
    PRODUCTION_IMPACT = "PRODUCTION_IMPACT"


class AccessRiskFactor(BaseModel):
    """Contributing factor to access risk score."""
    dimension: AccessRiskDimension
    score: float  # 0.0 to 100.0
    weight: float = 1.0
    description: str


class AccessRiskProfile(BaseModel):
    """Access Risk Profile for an Identity or Resource."""
    profile_id: str = Field(default_factory=lambda: f"risk_prof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    target_type: str  # IDENTITY, ENTITLEMENT, RESOURCE
    overall_risk_score: float = 0.0  # 0.0 to 100.0
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    factors: List[AccessRiskFactor] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessRiskAssessment(BaseModel):
    """Access Risk Assessment Outcome."""
    assessment_id: str = Field(default_factory=lambda: f"risk_eval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    subject_identity_id: str
    resource_id: str
    composite_risk_score: float = 0.0
    exceeds_threshold: bool = False
    threshold: float = 75.0
    risk_profile: AccessRiskProfile


class AccessRiskManager:
    """Composes with platform RiskManager to evaluate access risk."""

    def __init__(self) -> None:
        self._profiles: Dict[str, AccessRiskProfile] = {}
        self._assessments: Dict[str, AccessRiskAssessment] = {}

    def calculate_risk(
        self,
        tenant_id: str,
        subject_identity_id: str,
        resource_id: str,
        privilege_score: float = 50.0,
        resource_sensitivity_score: float = 50.0,
        identity_trust_score: float = 80.0,
        has_toxic_combinations: bool = False,
        is_production: bool = False,
        threshold: float = 75.0,
    ) -> AccessRiskAssessment:
        factors = [
            AccessRiskFactor(dimension=AccessRiskDimension.PRIVILEGE_LEVEL, score=privilege_score, weight=1.2, description="Privilege elevation score"),
            AccessRiskFactor(dimension=AccessRiskDimension.RESOURCE_SENSITIVITY, score=resource_sensitivity_score, weight=1.5, description="Sensitivity level of target resource"),
            AccessRiskFactor(dimension=AccessRiskDimension.IDENTITY_TRUST, score=100.0 - identity_trust_score, weight=1.0, description="Inverse identity trust score"),
        ]

        if has_toxic_combinations:
            factors.append(AccessRiskFactor(dimension=AccessRiskDimension.TOXIC_COMBINATION, score=90.0, weight=2.0, description="Segregation of duties violation detected"))

        if is_production:
            factors.append(AccessRiskFactor(dimension=AccessRiskDimension.PRODUCTION_IMPACT, score=85.0, weight=1.5, description="Target is a production resource"))

        total_weighted_score = sum(f.score * f.weight for f in factors)
        total_weight = sum(f.weight for f in factors)
        composite = round(total_weighted_score / total_weight, 2) if total_weight > 0 else 0.0

        if composite >= 80.0:
            level = "CRITICAL"
        elif composite >= 60.0:
            level = "HIGH"
        elif composite >= 40.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        prof = AccessRiskProfile(
            tenant_id=tenant_id,
            target_id=subject_identity_id,
            target_type="IDENTITY",
            overall_risk_score=composite,
            risk_level=level,
            factors=factors,
        )
        self._profiles[prof.profile_id] = prof

        exceeds = composite > threshold

        asm = AccessRiskAssessment(
            tenant_id=tenant_id,
            subject_identity_id=subject_identity_id,
            resource_id=resource_id,
            composite_risk_score=composite,
            exceeds_threshold=exceeds,
            threshold=threshold,
            risk_profile=prof,
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> AccessRiskAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return asm
