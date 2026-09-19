"""Continuous Identity Assurance Engine."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class AssuranceDimension(str, Enum):
    TRUST = "TRUST"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    PRIVILEGE = "PRIVILEGE"
    BEHAVIOR = "BEHAVIOR"
    COMPLIANCE = "COMPLIANCE"
    EVIDENCE = "EVIDENCE"


class AssuranceStatus(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MARGINAL = "MARGINAL"
    POOR = "POOR"
    CRITICAL = "CRITICAL"


class AssuranceFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dimension: AssuranceDimension
    description: str
    impact_score: float = 0.1


class IdentityAssuranceScore(BaseModel):
    score_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    overall_assurance_score: float = 0.90
    dimension_scores: Dict[AssuranceDimension, float] = Field(default_factory=dict)
    status: AssuranceStatus = AssuranceStatus.GOOD
    findings: List[AssuranceFinding] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityAssuranceEngine:
    """Evaluates continuous identity assurance posture."""

    def __init__(self) -> None:
        self._scores: Dict[str, IdentityAssuranceScore] = {}

    def assess_assurance(
        self,
        tenant_id: str,
        identity_id: str,
        trust_score: float = 0.90,
        mfa_enabled: bool = True,
        privilege_risk: float = 0.1,
    ) -> IdentityAssuranceScore:
        dim_scores = {
            AssuranceDimension.TRUST: trust_score,
            AssuranceDimension.AUTHENTICATION: 0.95 if mfa_enabled else 0.40,
            AssuranceDimension.AUTHORIZATION: 0.88,
            AssuranceDimension.PRIVILEGE: max(0.0, 1.0 - privilege_risk),
            AssuranceDimension.BEHAVIOR: 0.92,
            AssuranceDimension.COMPLIANCE: 0.90,
            AssuranceDimension.EVIDENCE: 0.96,
        }

        avg_score = round(sum(dim_scores.values()) / len(dim_scores), 4)

        status = (
            AssuranceStatus.EXCELLENT
            if avg_score >= 0.90
            else (
                AssuranceStatus.GOOD
                if avg_score >= 0.75
                else (
                    AssuranceStatus.MARGINAL
                    if avg_score >= 0.60
                    else (AssuranceStatus.POOR if avg_score >= 0.40 else AssuranceStatus.CRITICAL)
                )
            )
        )

        score_obj = IdentityAssuranceScore(
            identity_id=identity_id,
            tenant_id=tenant_id,
            overall_assurance_score=avg_score,
            dimension_scores=dim_scores,
            status=status,
        )
        self._scores[identity_id] = score_obj
        return score_obj

    def get_assurance_score(self, tenant_id: str, identity_id: str) -> IdentityAssuranceScore:
        score = self._scores.get(identity_id)
        if not score or score.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return score
