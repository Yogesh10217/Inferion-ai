"""Lifecycle Learning & Improvement Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field


class LifecycleRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"lrec_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    action_type: str


class LifecyclePattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"lpat_{uuid.uuid4().hex[:12]}")
    pattern_name: str
    occurrences: int = 1


class LifecycleLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"llr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    pattern: LifecyclePattern
    recommendations: List[LifecycleRecommendation] = Field(default_factory=list)
    learned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LifecycleLearningManager:
    """Extracts tenant-isolated lifecycle learning insights and recommendations."""

    def __init__(self) -> None:
        self._records: Dict[str, LifecycleLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        asset_id: str,
        pattern_name: str,
        recommendation_title: str,
    ) -> LifecycleLearningRecord:
        pat = LifecyclePattern(pattern_name=pattern_name)
        rec = LifecycleRecommendation(title=recommendation_title, description=f"Recommended action for {pattern_name}", action_type="UPDATE_EVALUATION_THRESHOLD")
        record = LifecycleLearningRecord(
            tenant_id=tenant_id,
            asset_id=asset_id,
            pattern=pat,
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def list_learnings(self, tenant_id: str) -> List[LifecycleLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
