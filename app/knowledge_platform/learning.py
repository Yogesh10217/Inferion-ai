"""Continuous Learning & Feedback Intelligence Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.knowledge import KnowledgeManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeFeedbackType(str, Enum):
    HELPFUL = "HELPFUL"
    NOT_HELPFUL = "NOT_HELPFUL"
    INCORRECT = "INCORRECT"
    OUTDATED = "OUTDATED"
    INCOMPLETE = "INCOMPLETE"
    CONTRADICTORY = "CONTRADICTORY"


class KnowledgeFeedback(BaseModel):
    feedback_id: str = Field(default_factory=lambda: f"fb_{uuid.uuid4().hex[:10]}")
    item_id: str
    feedback_type: KnowledgeFeedbackType = KnowledgeFeedbackType.HELPFUL
    submitted_by: str = "user"
    comments: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class KnowledgeLearningEngine:
    """Processes user, agent, and workflow feedback, adjusting confidence scores without mutating immutable history."""

    def __init__(self, knowledge_manager: Optional[KnowledgeManager] = None) -> None:
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self._feedback_store: List[KnowledgeFeedback] = []

    def submit_feedback(self, item_id: str, feedback_type: KnowledgeFeedbackType, submitted_by: str = "user", comments: Optional[str] = None) -> KnowledgeFeedback:
        fb = KnowledgeFeedback(item_id=item_id, feedback_type=feedback_type, submitted_by=submitted_by, comments=comments)
        self._feedback_store.append(fb)

        # Adjust item confidence score
        try:
            item = self.knowledge_manager.get_item(item_id)
            if feedback_type == KnowledgeFeedbackType.HELPFUL:
                item.confidence_score = min(1.0, round(item.confidence_score + 0.05, 2))
            elif feedback_type in (KnowledgeFeedbackType.INCORRECT, KnowledgeFeedbackType.OUTDATED):
                item.confidence_score = max(0.0, round(item.confidence_score - 0.20, 2))
            logger.info(f"[LEARNING ENGINE] Applied feedback '{feedback_type.value}' to item '{item_id}': New confidence = {item.confidence_score}")
        except Exception as e:
            logger.warning(f"[LEARNING ENGINE] Could not update item confidence: {e}")

        return fb
