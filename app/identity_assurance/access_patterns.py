"""Access Behavior Intelligence."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class AccessPatternType(str, Enum):
    READ_HEAVY = "READ_HEAVY"
    WRITE_HEAVY = "WRITE_HEAVY"
    UNUSUAL_HOURS = "UNUSUAL_HOURS"
    HIGH_FREQUENCY = "HIGH_FREQUENCY"
    BATCH_EXPORT = "BATCH_EXPORT"
    NORMAL = "NORMAL"


class AccessPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: AccessPatternType = AccessPatternType.NORMAL
    frequency_per_hour: float = 10.0
    resource_category: str = "general"
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessPatternAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    patterns: List[AccessPattern] = Field(default_factory=list)
    risk_score: float = 0.1
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessPatternManager:
    """Analyzes access frequency, patterns, and anomalies."""

    def __init__(self) -> None:
        self._assessments: Dict[str, AccessPatternAssessment] = {}

    def assess_patterns(
        self,
        tenant_id: str,
        identity_id: str,
        patterns: Optional[List[AccessPattern]] = None,
    ) -> AccessPatternAssessment:
        p_list = patterns or [AccessPattern(pattern_type=AccessPatternType.NORMAL)]
        high_risk_p = any(p.pattern_type in [AccessPatternType.UNUSUAL_HOURS, AccessPatternType.BATCH_EXPORT] for p in p_list)

        assessment = AccessPatternAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            patterns=p_list,
            risk_score=0.7 if high_risk_p else 0.1,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> AccessPatternAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
