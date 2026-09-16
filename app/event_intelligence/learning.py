"""Event Intelligence Learning Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field


class EventRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"erec_{uuid.uuid4().hex[:12]}")
    title: str
    target_subsystem: str
    description: str


class EventPatternLearning(BaseModel):
    pattern_name: str
    frequency: int = 1


class EventLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"elr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    pattern: EventPatternLearning
    recommendations: List[EventRecommendation] = Field(default_factory=list)
    learned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventLearningManager:
    """Generates tenant-scoped learning records and non-mutating platform recommendations."""

    def __init__(self) -> None:
        self._records: Dict[str, EventLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        pattern_name: str,
        recommendation_title: str,
        target_subsystem: str = "RELIABILITY_PLATFORM",
    ) -> EventLearningRecord:
        pat = EventPatternLearning(pattern_name=pattern_name)
        rec = EventRecommendation(
            title=recommendation_title,
            target_subsystem=target_subsystem,
            description=f"Recommended improvement for {pattern_name}",
        )
        record = EventLearningRecord(tenant_id=tenant_id, pattern=pat, recommendations=[rec])
        self._records[record.record_id] = record
        return record

    def list_learnings(self, tenant_id: str) -> List[EventLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
