"""Operational Learning Intelligence (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class OperationalLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_op_{uuid.uuid4().hex[:8]}")
    title: str
    suggested_action: str
    target_service_id: str
    auto_execute: bool = False  # MUST be False! Advisory recommendations only.


class OperationalLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"lrn_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    pattern_name: str
    description: str
    recommendations: List[OperationalLearningRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalLearningManager:
    """Manages operational learning recommendations (advisory only, auto_execute=False)."""

    def __init__(self) -> None:
        self._records: Dict[str, OperationalLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        pattern_name: str,
        description: str,
        recommendation_title: str,
        suggested_action: str,
        target_service_id: str,
    ) -> OperationalLearningRecord:
        rec = OperationalLearningRecommendation(
            title=recommendation_title,
            suggested_action=suggested_action,
            target_service_id=target_service_id,
            auto_execute=False,  # Enforce non-mutating invariant!
        )
        record = OperationalLearningRecord(
            tenant_id=tenant_id,
            pattern_name=pattern_name,
            description=description,
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def get_record(self, tenant_id: str, record_id: str) -> OperationalLearningRecord:
        rec = self._records.get(record_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return rec
