"""Integration Learning Intelligence (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class IntegrationPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"pat_int_{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    observed_occurrences: int = 1


class IntegrationRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_int_{uuid.uuid4().hex[:8]}")
    title: str
    suggested_action: str
    target_connector_id: Optional[str] = None
    target_workflow_id: Optional[str] = None
    auto_execute: bool = False  # MUST be False! Advisory recommendations only.


class IntegrationLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"lrn_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    patterns: List[IntegrationPattern] = Field(default_factory=list)
    recommendations: List[IntegrationRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationLearningManager:
    """Manages integration learning recommendations (non-mutating, advisory only)."""

    def __init__(self) -> None:
        self._records: Dict[str, IntegrationLearningRecord] = {}

    def record_learning_pattern(
        self,
        tenant_id: str,
        pattern_name: str,
        description: str,
        recommendation_title: str,
        suggested_action: str,
        target_connector_id: Optional[str] = None,
        target_workflow_id: Optional[str] = None,
    ) -> IntegrationLearningRecord:
        pattern = IntegrationPattern(name=pattern_name, description=description)
        rec = IntegrationRecommendation(
            title=recommendation_title,
            suggested_action=suggested_action,
            target_connector_id=target_connector_id,
            target_workflow_id=target_workflow_id,
            auto_execute=False,  # Enforces non-mutating learning invariant!
        )
        record = IntegrationLearningRecord(
            tenant_id=tenant_id,
            patterns=[pattern],
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def get_record(self, tenant_id: str, record_id: str) -> IntegrationLearningRecord:
        rec = self._records.get(record_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return rec

    def list_records(self, tenant_id: str) -> List[IntegrationLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
