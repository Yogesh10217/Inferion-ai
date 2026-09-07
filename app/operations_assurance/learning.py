"""Advisory operational learning with mandatory auto_execute = False enforcement."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException


class OperationalLearningPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    pattern_name: str
    trigger_condition: str
    observed_frequency: int = 1
    confidence: float = 0.8


class OperationalLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    title: str
    suggested_action: str
    auto_execute: bool = False  # MANDATORY INVARIANT: auto_execute = False


class OperationalLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    event_summary: str
    learned_insight: str
    auto_execute: bool = False  # MANDATORY INVARIANT: auto_execute = False
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsLearningManager:
    """Manages advisory operational learning patterns and recommendations. Enforces auto_execute = False."""

    def __init__(self) -> None:
        self._records: Dict[str, Dict[str, OperationalLearningRecord]] = {}  # tenant_id -> {record_id: record}

    def record_learning(
        self,
        tenant_id: str,
        service_id: str,
        event_summary: str,
        learned_insight: str,
    ) -> OperationalLearningRecord:
        record = OperationalLearningRecord(
            tenant_id=tenant_id,
            service_id=service_id,
            event_summary=event_summary,
            learned_insight=learned_insight,
            auto_execute=False,  # Enforce mandatory invariant!
        )
        if tenant_id not in self._records:
            self._records[tenant_id] = {}
        self._records[tenant_id][record.record_id] = record
        return record

    def list_learnings(self, tenant_id: str, service_id: Optional[str] = None) -> List[OperationalLearningRecord]:
        tenant_records = self._records.get(tenant_id, {})
        if service_id:
            return [r for r in tenant_records.values() if r.service_id == service_id]
        return list(tenant_records.values())
