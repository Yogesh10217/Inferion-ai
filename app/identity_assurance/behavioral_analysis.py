"""Identity Behavioral Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class BehaviorBaseline(BaseModel):
    baseline_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    typical_hours: List[int] = Field(default_factory=lambda: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
    typical_ip_ranges: List[str] = Field(default_factory=lambda: ["10.0.0.0/8"])
    avg_requests_per_day: float = 150.0


class BehaviorDeviation(BaseModel):
    deviation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deviation_type: str  # OFF_HOURS, UNUSUAL_LOCATION, EXCESSIVE_VOLUME
    severity: str = "LOW"
    score: float = 0.2


class IdentityBehavior(BaseModel):
    identity_id: str
    baseline: BehaviorBaseline = Field(default_factory=BehaviorBaseline)
    deviations: List[BehaviorDeviation] = Field(default_factory=list)


class BehaviorAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    behavior: IdentityBehavior
    anomaly_score: float = 0.1
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityBehaviorManager:
    """Manages identity behavioral baselines and deviation detection."""

    def __init__(self) -> None:
        self._assessments: Dict[str, BehaviorAssessment] = {}

    def assess_behavior(
        self,
        tenant_id: str,
        identity_id: str,
        deviations: Optional[List[BehaviorDeviation]] = None,
    ) -> BehaviorAssessment:
        dev_list = deviations or []
        anomaly_score = min(1.0, sum(d.score for d in dev_list)) if dev_list else 0.05

        behavior = IdentityBehavior(
            identity_id=identity_id,
            deviations=dev_list,
        )

        assessment = BehaviorAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            behavior=behavior,
            anomaly_score=round(anomaly_score, 4),
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> BehaviorAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
