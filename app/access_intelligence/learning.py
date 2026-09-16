"""Tenant-Scoped Access Intelligence Learning (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class AccessPattern(BaseModel):
    """Observed access pattern across identities or services."""
    pattern_id: str = Field(default_factory=lambda: f"pat_{uuid.uuid4().hex[:8]}")
    pattern_name: str
    frequency_count: int = 1
    description: str


class AccessLearningRecommendation(BaseModel):
    """Non-mutating learning recommendation."""
    recommendation_id: str = Field(default_factory=lambda: f"lrn_rec_{uuid.uuid4().hex[:8]}")
    target_identity_id: str
    recommended_action: str  # e.g., "CONSIDER_REVOKING_ROLE", "REVIEW_JIT_ACCESS_PATTERN"
    reasoning: str
    confidence_score: float = 85.0
    auto_execute: bool = False  # MUST ALWAYS BE FALSE


class AccessLearningRecord(BaseModel):
    """Access Learning Record Representation."""
    record_id: str = Field(default_factory=lambda: f"lrn_rec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    identity_id: str
    observed_patterns: List[AccessPattern] = Field(default_factory=list)
    recommendations: List[AccessLearningRecommendation] = Field(default_factory=list)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessLearningManager:
    """Manages tenant-scoped learning recommendations for access optimization (advisory only)."""

    def __init__(self) -> None:
        self._records: Dict[str, AccessLearningRecord] = {}

    def record_access_pattern(
        self,
        tenant_id: str,
        identity_id: str,
        pattern_name: str,
        description: str,
        recommended_action: str,
        reasoning: str,
        confidence_score: float = 85.0,
    ) -> AccessLearningRecord:
        pattern = AccessPattern(
            pattern_name=pattern_name,
            description=description,
        )
        # Learning MUST NOT automatically grant permissions or modify privileges.
        rec = AccessLearningRecommendation(
            target_identity_id=identity_id,
            recommended_action=recommended_action,
            reasoning=reasoning,
            confidence_score=confidence_score,
            auto_execute=False,  # Enforced invariant
        )
        record = AccessLearningRecord(
            tenant_id=tenant_id,
            identity_id=identity_id,
            observed_patterns=[pattern],
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def get_record(self, tenant_id: str, record_id: str) -> AccessLearningRecord:
        rec = self._records.get(record_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return rec

    def list_records(self, tenant_id: str) -> List[AccessLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
