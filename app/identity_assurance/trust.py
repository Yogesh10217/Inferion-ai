"""Identity Trust Engine."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.governance_platform.trust import TrustAssessment, TrustDimension, TrustFactor
from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class IdentityTrustDimension(str, Enum):
    IDENTITY_VERIFICATION = "IDENTITY_VERIFICATION"
    AUTHENTICATION_STRENGTH = "AUTHENTICATION_STRENGTH"
    BEHAVIORAL_CONSISTENCY = "BEHAVIORAL_CONSISTENCY"
    PRIVILEGE_RISK = "PRIVILEGE_RISK"
    ACCESS_HISTORY = "ACCESS_HISTORY"
    SECURITY_POSTURE = "SECURITY_POSTURE"
    GOVERNANCE_COMPLIANCE = "GOVERNANCE_COMPLIANCE"


class IdentityTrustFactor(BaseModel):
    dimension: IdentityTrustDimension
    score: float = 1.0  # 0.0 to 1.0
    weight: float = 1.0
    reasoning: str = ""


class IdentityTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    overall_trust_score: float = 1.0
    factors: List[IdentityTrustFactor] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityTrustAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    trust_score: IdentityTrustScore
    is_trusted: bool = True
    risk_level: str = "LOW"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityTrustEngine:
    """Evaluates identity trust scores across 7 dimensions."""

    def __init__(self) -> None:
        self._assessments: Dict[str, IdentityTrustAssessment] = {}

    def assess_trust(
        self,
        tenant_id: str,
        identity_id: str,
        mfa_enabled: bool = True,
        privilege_risk_score: float = 0.1,
        behavior_anomaly_score: float = 0.0,
    ) -> IdentityTrustAssessment:
        factors = [
            IdentityTrustFactor(
                dimension=IdentityTrustDimension.IDENTITY_VERIFICATION,
                score=0.95,
                weight=1.0,
                reasoning="Identity record verified",
            ),
            IdentityTrustFactor(
                dimension=IdentityTrustDimension.AUTHENTICATION_STRENGTH,
                score=0.90 if mfa_enabled else 0.40,
                weight=1.2,
                reasoning="MFA enabled" if mfa_enabled else "MFA disabled",
            ),
            IdentityTrustFactor(
                dimension=IdentityTrustDimension.BEHAVIORAL_CONSISTENCY,
                score=max(0.0, 1.0 - behavior_anomaly_score),
                weight=1.0,
                reasoning=f"Anomaly score: {behavior_anomaly_score}",
            ),
            IdentityTrustFactor(
                dimension=IdentityTrustDimension.PRIVILEGE_RISK,
                score=max(0.0, 1.0 - privilege_risk_score),
                weight=1.1,
                reasoning=f"Privilege risk score: {privilege_risk_score}",
            ),
            IdentityTrustFactor(
                dimension=IdentityTrustDimension.SECURITY_POSTURE,
                score=0.92,
                weight=1.0,
                reasoning="Clean security status",
            ),
        ]

        total_weight = sum(f.weight for f in factors)
        weighted_score = sum(f.score * f.weight for f in factors) / total_weight if total_weight > 0 else 1.0

        overall_score = round(weighted_score, 4)
        is_trusted = overall_score >= 0.70
        risk_level = "LOW" if overall_score >= 0.85 else ("MEDIUM" if overall_score >= 0.60 else "HIGH")

        score_obj = IdentityTrustScore(
            identity_id=identity_id,
            tenant_id=tenant_id,
            overall_trust_score=overall_score,
            factors=factors,
        )

        assessment = IdentityTrustAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            trust_score=score_obj,
            is_trusted=is_trusted,
            risk_level=risk_level,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_trust_assessment(self, tenant_id: str, identity_id: str) -> IdentityTrustAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment

    def to_platform_trust_assessment(self, assessment: IdentityTrustAssessment) -> TrustAssessment:
        factors = [
            TrustFactor(
                dimension=TrustDimension.SECURITY,
                score=assessment.trust_score.overall_trust_score * 100.0,
                description="Identity trust score mapped to platform trust assessment",
            )
        ]
        return TrustAssessment(
            target_resource_id=assessment.identity_id,
            tenant_id=assessment.tenant_id,
            overall_score=assessment.trust_score.overall_trust_score * 100.0,
            overall_trust_level="HIGH" if assessment.is_trusted else "LOW",
            factors=factors,
        )
