"""Least Privilege Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class PrivilegeReductionRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_permission: str
    target_resource: str
    reasoning: str
    auto_execute: bool = False  # Mandatory rule: auto_execute = False


class LeastPrivilegeRisk(BaseModel):
    over_privileged_score: float = 0.2  # 0.0 to 1.0
    unused_permissions: List[str] = Field(default_factory=list)


class LeastPrivilegeAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    risk: LeastPrivilegeRisk = Field(default_factory=LeastPrivilegeRisk)
    recommendations: List[PrivilegeReductionRecommendation] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LeastPrivilegeManager:
    """Evaluates least privilege posture and generates advisory recommendations only."""

    def __init__(self) -> None:
        self._assessments: Dict[str, LeastPrivilegeAssessment] = {}

    def assess_least_privilege(
        self,
        tenant_id: str,
        identity_id: str,
        active_permissions: List[str],
        used_permissions: List[str],
    ) -> LeastPrivilegeAssessment:
        unused = [p for p in active_permissions if p not in used_permissions]
        over_priv_score = len(unused) / len(active_permissions) if active_permissions else 0.0

        recommendations = [
            PrivilegeReductionRecommendation(
                target_permission=p,
                target_resource="*",
                reasoning=f"Permission '{p}' unused in last 90 days",
                auto_execute=False,
            )
            for p in unused
        ]

        risk = LeastPrivilegeRisk(
            over_privileged_score=round(over_priv_score, 4),
            unused_permissions=unused,
        )

        assessment = LeastPrivilegeAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            risk=risk,
            recommendations=recommendations,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> LeastPrivilegeAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
