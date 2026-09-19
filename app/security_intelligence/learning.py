"""Tenant-Scoped Security Learning Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field


class SecurityRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    action_type: str


class SecurityPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"secpat_{uuid.uuid4().hex[:12]}")
    pattern_name: str
    recurrence_count: int = 1


class SecurityLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"slr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    pattern: SecurityPattern
    recommendations: List[SecurityRecommendation] = Field(default_factory=list)
    learned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityLearningManager:
    """Extracts tenant-isolated security learning insights without executing automated mutations."""

    def __init__(self) -> None:
        self._records: Dict[str, SecurityLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        incident_id: str,
        pattern_name: str,
        recommendation_title: str,
    ) -> SecurityLearningRecord:
        pat = SecurityPattern(pattern_name=pattern_name)
        rec = SecurityRecommendation(
            title=recommendation_title, description=f"Recommended action for {pattern_name}", action_type="TUNE_POLICY"
        )
        record = SecurityLearningRecord(
            tenant_id=tenant_id,
            incident_id=incident_id,
            pattern=pat,
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def list_learnings(self, tenant_id: str) -> List[SecurityLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
