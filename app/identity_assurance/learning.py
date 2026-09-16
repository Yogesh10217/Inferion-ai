"""Advisory Identity Learning Subsystem."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class IdentityLearningPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pattern_name: str
    observed_frequency: int = 1
    confidence: float = 0.85


class IdentityLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    target_identity_id: str
    suggested_action: str
    auto_execute: bool = False  # MANDATORY INVARIANT: auto_execute = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    patterns: List[IdentityLearningPattern] = Field(default_factory=list)
    recommendations: List[IdentityLearningRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityLearningManager:
    """Manages advisory identity learning recommendations enforcing auto_execute = False."""

    def __init__(self) -> None:
        self._records: Dict[str, IdentityLearningRecord] = {}

    def generate_recommendations(
        self,
        tenant_id: str,
        identity_id: str,
        title: str = "Optimize Privilege Scope",
        suggested_action: str = "RECOMMEND_ROLE_REDUCTION",
    ) -> IdentityLearningRecord:
        rec = IdentityLearningRecommendation(
            title=title,
            description="Advisory learning recommendation based on access history analysis.",
            target_identity_id=identity_id,
            suggested_action=suggested_action,
            auto_execute=False,  # Enforce advisory only
        )

        pattern = IdentityLearningPattern(
            pattern_name="Over-privileged service identity access pattern",
            observed_frequency=5,
        )

        record = IdentityLearningRecord(
            tenant_id=tenant_id,
            patterns=[pattern],
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def get_record(self, tenant_id: str, record_id: str) -> IdentityLearningRecord:
        record = self._records.get(record_id)
        if not record or record.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return record
