"""Knowledge Learning Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field


class KnowledgeLearningSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"lsig_{uuid.uuid4().hex[:8]}")
    signal_type: str = "RETRIEVAL_FEEDBACK"
    description: str
    weight: float = 1.0


class KnowledgePattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"kpat_{uuid.uuid4().hex[:8]}")
    pattern_name: str
    frequency: int = 1
    confidence: float = 0.90


class KnowledgeLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"lrec_{uuid.uuid4().hex[:8]}")
    action: str
    reason: str


class KnowledgeLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"klearn_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    signals: List[KnowledgeLearningSignal] = Field(default_factory=list)
    patterns: List[KnowledgePattern] = Field(default_factory=list)
    recommendations: List[KnowledgeLearningRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeLearningManager:
    """Extracts tenant-isolated knowledge learning patterns and produces non-mutating recommendations."""

    def __init__(self) -> None:
        self._records: Dict[str, KnowledgeLearningRecord] = {}

    def record_learning(
        self,
        tenant_id: str,
        target_id: str,
        feedback_signal: str = "RETRIEVAL_SUCCESS",
        pattern_name: str = "FREQUENTLY_ACCESSED_KNOWLEDGE",
    ) -> KnowledgeLearningRecord:
        sig = KnowledgeLearningSignal(description=feedback_signal)
        pat = KnowledgePattern(pattern_name=pattern_name, frequency=1)
        rec = KnowledgeLearningRecommendation(
            action="PIN_KNOWLEDGE_CONTEXT",
            reason=f"High usage pattern '{pattern_name}' detected.",
        )
        rec_obj = KnowledgeLearningRecord(
            tenant_id=tenant_id,
            target_id=target_id,
            signals=[sig],
            patterns=[pat],
            recommendations=[rec],
        )
        self._records[rec_obj.record_id] = rec_obj
        return rec_obj

    def list_records(self, tenant_id: str) -> List[KnowledgeLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
