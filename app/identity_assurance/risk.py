"""Identity Risk Intelligence."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException
from app.governance_platform.risk import RiskManager


class IdentityRiskDimension(str, Enum):
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    PRIVILEGE = "PRIVILEGE"
    BEHAVIOR = "BEHAVIOR"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    OPERATIONAL = "OPERATIONAL"
    CROSS_DOMAIN = "CROSS_DOMAIN"


class IdentityRiskFactor(BaseModel):
    dimension: IdentityRiskDimension
    risk_score: float = 0.1
    weight: float = 1.0
    description: str = ""


class IdentityRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    overall_risk_score: float = 0.1
    factors: List[IdentityRiskFactor] = Field(default_factory=list)


class IdentityRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    risk_profile: IdentityRiskProfile
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityRiskManager:
    """Manages identity risk assessments using platform RiskManager."""

    def __init__(self, risk_manager: Optional[RiskManager] = None) -> None:
        self.risk_manager = risk_manager or RiskManager()
        self._assessments: Dict[str, IdentityRiskAssessment] = {}

    def assess_risk(
        self,
        tenant_id: str,
        identity_id: str,
        factors: Optional[List[IdentityRiskFactor]] = None,
    ) -> IdentityRiskAssessment:
        fact_list = factors or [
            IdentityRiskFactor(
                dimension=IdentityRiskDimension.AUTHENTICATION,
                risk_score=0.1,
                description="MFA enabled",
            ),
            IdentityRiskFactor(
                dimension=IdentityRiskDimension.PRIVILEGE,
                risk_score=0.2,
                description="Standard privilege scope",
            ),
        ]

        total_w = sum(f.weight for f in fact_list)
        weighted_r = sum(f.risk_score * f.weight for f in fact_list) / total_w if total_w > 0 else 0.1
        overall_score = round(weighted_r, 4)

        risk_level = "CRITICAL" if overall_score >= 0.8 else ("HIGH" if overall_score >= 0.6 else ("MEDIUM" if overall_score >= 0.3 else "LOW"))

        profile = IdentityRiskProfile(
            identity_id=identity_id,
            tenant_id=tenant_id,
            overall_risk_score=overall_score,
            factors=fact_list,
        )

        assessment = IdentityRiskAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            risk_profile=profile,
            risk_level=risk_level,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> IdentityRiskAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
