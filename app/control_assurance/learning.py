"""Continuous Control Improvement Intelligence Subsystem (Phase 5.38)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard


class ControlPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"pat_{uuid.uuid4().hex[:12]}")
    pattern_name: str
    frequency: int = 1
    description: str


class ControlRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    control_id: str
    suggested_action: str
    auto_execute: bool = False
    requires_approval: bool = True
    justification: str


class ControlLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"lrec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    patterns: List[ControlPattern] = Field(default_factory=list)
    recommendations: List[ControlRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlLearningManager:
    """Generates advisory recommendations without auto-execution or auto-modification."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._records: Dict[str, ControlLearningRecord] = {}

    def record_learning(self, tenant_id: str, control_id: str, observation: str) -> ControlLearningRecord:
        rec = ControlRecommendation(
            control_id=control_id,
            suggested_action="Adjust evaluation frequency from 60m to 15m based on signal frequency",
            auto_execute=False,
            requires_approval=True,
            justification=f"Observation: {observation}",
        )

        pat = ControlPattern(
            pattern_name="Frequent Evaluation Warning Pattern",
            frequency=3,
            description=observation,
        )

        record = ControlLearningRecord(
            tenant_id=tenant_id,
            control_id=control_id,
            patterns=[pat],
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record
