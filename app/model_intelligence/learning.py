"""Advisory Model Intelligence Learning (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelLearningPattern(BaseModel):
    pattern_id: str
    pattern_name: str
    description: str
    frequency: int = 1


class ModelLearningRecommendation(BaseModel):
    recommendation_id: str
    target_model_id: str
    recommendation: str
    reasoning: str
    impact: str = "MEDIUM"
    auto_execute: bool = False  # MANDATORY: auto_execute MUST ALWAYS be False


class ModelLearningRecord(BaseModel):
    record_id: str
    tenant_id: str
    pattern: ModelLearningPattern
    recommendation: ModelLearningRecommendation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelLearningManager:
    """Manages advisory learning recommendations for model intelligence.

    MANDATORY INVARIANT: auto_execute MUST ALWAYS be False.
    Learning MUST NEVER deploy models, modify models, change routing, or retrain models automatically.
    """

    def __init__(self) -> None:
        self._records: Dict[str, ModelLearningRecord] = {}

    def generate_recommendation(
        self,
        target_model_id: str,
        tenant_id: str,
        pattern_name: str,
        recommendation_text: str,
        reasoning: str,
    ) -> ModelLearningRecord:
        rec_id = f"mlearn-{uuid.uuid4().hex[:8]}"

        pattern = ModelLearningPattern(
            pattern_id=f"pat-{uuid.uuid4().hex[:6]}",
            pattern_name=pattern_name,
            description=reasoning,
        )

        rec = ModelLearningRecommendation(
            recommendation_id=f"rec-{uuid.uuid4().hex[:6]}",
            target_model_id=target_model_id,
            recommendation=recommendation_text,
            reasoning=reasoning,
            auto_execute=False,  # Enforce invariant strictly
        )

        record = ModelLearningRecord(
            record_id=rec_id,
            tenant_id=tenant_id,
            pattern=pattern,
            recommendation=rec,
        )

        self._records[rec_id] = record
        logger.info(f"[MODEL LEARNING] Generated advisory recommendation {rec_id} for model {target_model_id} (auto_execute=False)")
        return record

    def list_records(self, tenant_id: str) -> List[ModelLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
