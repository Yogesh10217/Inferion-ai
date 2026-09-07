"""Security Learning & Pattern Refinement Engine (Advisory Learning Invariant)."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class SecurityLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"sec-learn-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    incident_id: str
    learned_pattern: str
    recommended_rule_update: str
    auto_execute: bool = False  # MANDATORY INVARIANT: Always False (Human Advisory Only)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityLearningManager:
    """Derives learning insights from security incidents and posture trends strictly as advisory recommendations."""

    def __init__(self) -> None:
        self._records: Dict[str, SecurityLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        incident_id: str,
        learned_pattern: str,
        recommended_rule_update: str,
    ) -> SecurityLearningRecord:
        record = SecurityLearningRecord(
            tenant_id=tenant_id,
            incident_id=incident_id,
            learned_pattern=learned_pattern,
            recommended_rule_update=recommended_rule_update,
            auto_execute=False,  # Enforce auto_execute = False strictly
        )
        self._records[record.record_id] = record
        return record

    def list_learnings(self, tenant_id: str) -> List[SecurityLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
