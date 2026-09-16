"""Resilience Learning Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard


class ResiliencePattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"respat_{uuid.uuid4().hex[:8]}")
    service_id: str
    pattern_name: str
    frequency: int = 1
    description: str


class ResilienceRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"resrec_{uuid.uuid4().hex[:8]}")
    target_service_id: str
    suggested_action: str
    requires_approval: bool = True
    auto_execute: bool = False  # NEVER auto-execute


class ResilienceLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"reslearn_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    patterns: List[ResiliencePattern] = Field(default_factory=list)
    recommendations: List[ResilienceRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceLearningManager:
    """Resilience Learning Manager generating advisory recommendations without auto-executing production changes."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._records: Dict[str, ResilienceLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        service_id: str,
        failure_summary: str,
    ) -> ResilienceLearningRecord:
        pattern = ResiliencePattern(
            service_id=service_id,
            pattern_name="Recurring Capacity Saturation",
            description=failure_summary,
        )
        recommendation = ResilienceRecommendation(
            target_service_id=service_id,
            suggested_action="Adjust baseline minimum instance pool from 2 to 4",
            requires_approval=True,
            auto_execute=False,  # Enforce policy: never auto-execute
        )

        record = ResilienceLearningRecord(
            tenant_id=tenant_id,
            service_id=service_id,
            patterns=[pattern],
            recommendations=[recommendation],
        )
        self._records[record.record_id] = record
        return record
