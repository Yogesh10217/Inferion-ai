"""Advisory data learning (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DataLearningRecord(BaseModel):
    record_id: str
    tenant_id: str
    dataset_id: str
    observed_pattern: str
    confidence_score: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataLearningPattern(BaseModel):
    pattern_id: str
    name: str
    description: str
    frequency_count: int = 1


class DataLearningRecommendation(BaseModel):
    recommendation_id: str
    tenant_id: str
    dataset_id: str
    title: str
    recommendation_type: str
    proposed_action: str
    confidence: float = 0.85
    auto_execute: bool = False  # MUST ALWAYS be False
    reasoning: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataLearningManager:
    """Provides advisory pattern learning and recommendations (enforces auto_execute=False)."""

    def __init__(self) -> None:
        self._records: Dict[str, DataLearningRecord] = {}
        self._recommendations: Dict[str, DataLearningRecommendation] = {}

    def record_learning(
        self,
        tenant_id: str,
        dataset_id: str,
        observed_pattern: str,
        confidence_score: float = 0.85,
        record_id: Optional[str] = None,
    ) -> DataLearningRecord:
        rid = record_id or f"dlrec-{uuid.uuid4().hex[:8]}"
        rec = DataLearningRecord(
            record_id=rid,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            observed_pattern=observed_pattern,
            confidence_score=confidence_score,
        )
        self._records[rid] = rec
        return rec

    def generate_recommendation(
        self,
        tenant_id: str,
        dataset_id: str,
        title: str,
        recommendation_type: str,
        proposed_action: str,
        reasoning: str,
        confidence: float = 0.85,
        recommendation_id: Optional[str] = None,
    ) -> DataLearningRecommendation:
        rec_id = recommendation_id or f"dlrec-rec-{uuid.uuid4().hex[:8]}"

        # Enforce advisory safeguards: auto_execute is strictly False
        rec = DataLearningRecommendation(
            recommendation_id=rec_id,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            title=title,
            recommendation_type=recommendation_type,
            proposed_action=proposed_action,
            confidence=confidence,
            auto_execute=False,
            reasoning=reasoning,
        )
        self._recommendations[rec_id] = rec
        return rec

    def list_recommendations(self, tenant_id: str, dataset_id: Optional[str] = None) -> List[DataLearningRecommendation]:
        recs = [r for r in self._recommendations.values() if r.tenant_id == tenant_id]
        if dataset_id:
            recs = [r for r in recs if r.dataset_id == dataset_id]
        return recs
