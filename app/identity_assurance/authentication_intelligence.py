"""Authentication Posture Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class AuthenticationStrength(str, Enum):
    WEAK = "WEAK"
    MEDIUM = "MEDIUM"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


class AuthenticationMethodReference(BaseModel):
    method_type: str  # PASSWORD, MFA_TOTP, MFA_FIDO2, OAUTH_SSO, CERTIFICATE, API_KEY
    is_mfa: bool = False
    last_used: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthenticationRisk(BaseModel):
    risk_score: float = 0.0
    risk_factors: List[str] = Field(default_factory=list)
    has_anomaly: bool = False


class AuthenticationAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    strength: AuthenticationStrength = AuthenticationStrength.STRONG
    mfa_enabled: bool = True
    methods: List[AuthenticationMethodReference] = Field(default_factory=list)
    risk: AuthenticationRisk = Field(default_factory=AuthenticationRisk)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthenticationIntelligenceManager:
    """Analyzes authentication posture without storing credentials."""

    def __init__(self) -> None:
        self._assessments: Dict[str, AuthenticationAssessment] = {}

    def assess_authentication(
        self,
        tenant_id: str,
        identity_id: str,
        mfa_enabled: bool = True,
        methods: Optional[List[AuthenticationMethodReference]] = None,
    ) -> AuthenticationAssessment:
        method_list = methods or [
            AuthenticationMethodReference(method_type="MFA_TOTP", is_mfa=True)
        ]
        strength = (
            AuthenticationStrength.VERY_STRONG
            if any(m.method_type == "MFA_FIDO2" for m in method_list)
            else (AuthenticationStrength.STRONG if mfa_enabled else AuthenticationStrength.WEAK)
        )
        risk = AuthenticationRisk(
            risk_score=0.1 if mfa_enabled else 0.6,
            risk_factors=[] if mfa_enabled else ["No MFA configured"],
            has_anomaly=not mfa_enabled,
        )

        assessment = AuthenticationAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            strength=strength,
            mfa_enabled=mfa_enabled,
            methods=method_list,
            risk=risk,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> AuthenticationAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
