"""Decision Learning & Pattern Intelligence Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.outcomes import DecisionOutcome


class DecisionPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"pat_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    pattern_name: str
    description: str
    confidence_score: float = 85.0


class DecisionLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"learn_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    decision_id: str
    insight: str
    feedback_score: float = 90.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionLearningManager:
    """Processes historical decision outcomes to generate tenant-isolated feedback insights."""

    def __init__(self) -> None:
        self._records: Dict[str, List[DecisionLearningRecord]] = {}

    def process_outcome_learning(self, tenant_id: str, outcome: DecisionOutcome) -> DecisionLearningRecord:
        if outcome.actual_value_usd > outcome.expected_value_usd:
            insight = f"Decision '{outcome.decision_id}' exceeded value expectations by {((outcome.actual_value_usd - outcome.expected_value_usd)/outcome.expected_value_usd)*100:.1f}%."
            fb = 95.0
        else:
            insight = f"Decision '{outcome.decision_id}' achieved {outcome.status.value} status."
            fb = 85.0

        rec = DecisionLearningRecord(
            tenant_id=tenant_id,
            decision_id=outcome.decision_id,
            insight=insight,
            feedback_score=fb,
        )

        if tenant_id not in self._records:
            self._records[tenant_id] = []
        self._records[tenant_id].append(rec)
        return rec

    def list_learning_records(self, tenant_id: str) -> List[DecisionLearningRecord]:
        return self._records.get(tenant_id, [])
