"""Advisory decision learning intelligence. MANDATORY: auto_execute = False."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException


class DecisionLearningPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str
    trigger_signal_type: str
    observed_outcome: str
    success_rate: float = 0.9
    occurrence_count: int = 1


class DecisionLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    suggested_policy_update: str
    rationale: str
    auto_execute: bool = False  # MANDATORY: MUST ALWAYS BE FALSE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    decision_id: str
    patterns_identified: List[DecisionLearningPattern] = Field(default_factory=list)
    recommendations: List[DecisionLearningRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionLearningManager:
    """Manages advisory decision learning patterns. Never auto-executes."""

    def __init__(self) -> None:
        self._records: Dict[str, DecisionLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        decision_id: str,
        domain: str = "operations",
        trigger_signal_type: str = "COST_SPIKE",
        observed_outcome: str = "SUCCESS",
    ) -> DecisionLearningRecord:
        pattern = DecisionLearningPattern(
            domain=domain,
            trigger_signal_type=trigger_signal_type,
            observed_outcome=observed_outcome,
            success_rate=0.92,
            occurrence_count=5,
        )
        rec = DecisionLearningRecommendation(
            title=f"Adjust {domain} threshold for {trigger_signal_type}",
            suggested_policy_update="Lower cost anomaly threshold by 5%",
            rationale="Pattern identified 5 successful historical remediations",
            auto_execute=False,  # MANDATORY INVARIANT
        )

        record = DecisionLearningRecord(
            tenant_id=tenant_id,
            decision_id=decision_id,
            patterns_identified=[pattern],
            recommendations=[rec],
        )
        self._records[record.record_id] = record
        return record

    def list_records(self, tenant_id: str) -> List[DecisionLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
