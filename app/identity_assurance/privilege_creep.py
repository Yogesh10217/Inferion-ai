"""Privilege Creep Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class PrivilegeGrowth(BaseModel):
    timeframe_days: int = 90
    initial_privilege_count: int = 5
    current_privilege_count: int = 15
    growth_rate: float = 2.0  # 200% growth


class PrivilegeCreepRisk(BaseModel):
    has_creep: bool = False
    creep_score: float = 0.2  # 0.0 to 1.0
    risk_level: str = "LOW"


class PrivilegeCreepAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    growth: PrivilegeGrowth = Field(default_factory=PrivilegeGrowth)
    risk: PrivilegeCreepRisk = Field(default_factory=PrivilegeCreepRisk)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrivilegeCreepManager:
    """Analyzes historical privilege expansion to detect privilege creep."""

    def __init__(self) -> None:
        self._assessments: Dict[str, PrivilegeCreepAssessment] = {}

    def assess_privilege_creep(
        self,
        tenant_id: str,
        identity_id: str,
        initial_count: int = 5,
        current_count: int = 15,
        timeframe_days: int = 90,
    ) -> PrivilegeCreepAssessment:
        growth_rate = (current_count - initial_count) / max(1, initial_count)
        has_creep = growth_rate > 1.0 and current_count > 10
        creep_score = min(1.0, max(0.0, growth_rate / 3.0))

        growth = PrivilegeGrowth(
            timeframe_days=timeframe_days,
            initial_privilege_count=initial_count,
            current_privilege_count=current_count,
            growth_rate=round(growth_rate, 2),
        )

        risk = PrivilegeCreepRisk(
            has_creep=has_creep,
            creep_score=round(creep_score, 4),
            risk_level="HIGH" if creep_score > 0.6 else ("MEDIUM" if creep_score > 0.3 else "LOW"),
        )

        assessment = PrivilegeCreepAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            growth=growth,
            risk=risk,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> PrivilegeCreepAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
