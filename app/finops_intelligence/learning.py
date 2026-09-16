"""FinOps Learning Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class FinOpsLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_fin_{uuid.uuid4().hex[:8]}")
    title: str
    suggested_optimization: str
    target_resource_id: str
    auto_execute: bool = False  # MUST be False! Advisory recommendations only.


class FinOpsLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"lrn_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    pattern_name: str
    description: str
    recommendations: List[FinOpsLearningRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsLearningManager:
    """Manages advisory learning recommendations (auto_execute=False, no auto spending increase)."""

    def __init__(self) -> None:
        self._records: Dict[str, FinOpsLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        pattern_name: str,
        description: str,
        recommendation_title: str,
        suggested_optimization: str,
        target_resource_id: str,
    ) -> FinOpsLearningRecord:
        rec = FinOpsLearningRecommendation(
            title=recommendation_title,
            suggested_optimization=suggested_optimization,
            target_resource_id=target_resource_id,
            auto_execute=False,  # Enforce non-mutating invariant!
        )
        record = FinOpsLearningRecord(
            tenant_id=tenant_id,
            pattern_name=pattern_name,
            description=description,
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def get_record(self, tenant_id: str, record_id: str) -> FinOpsLearningRecord:
        rec = self._records.get(record_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return rec
