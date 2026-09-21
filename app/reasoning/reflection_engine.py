"""
Reflection & Self-Correction Engine
"""

import logging
import time
from typing import Any, Dict, List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LessonLearned(BaseModel):
    lesson_id: str
    episode_id: str
    category: str  # success, failure, optimization
    insight: str
    recommendation: str
    status: str = "pending_approval"  # pending_approval, approved, rejected
    created_at: float = Field(default_factory=time.time)


class ReflectionEngine:
    """Analyzes past execution trajectories to generate lessons learned and improvement recommendations."""

    def __init__(self):
        self._lessons_store: List[LessonLearned] = []

    def analyze_execution(
        self, episode_id: str, execution_trace: List[Dict[str, Any]], final_status: str
    ) -> Dict[str, Any]:
        """Perform post-execution reflection analysis."""
        failures = [step for step in execution_trace if step.get("status") in ("failed", "error")]
        successes = [step for step in execution_trace if step.get("status") == "completed"]

        lessons = []

        if final_status in ("failed", "error") or failures:
            insight = f"Detected {len(failures)} step failures during execution episode '{episode_id}'"
            rec = "Add automatic retry backoff and fallback tool selection for transient errors."
            lesson = LessonLearned(
                lesson_id=f"lesson_{int(time.time() * 1000)}_f",
                episode_id=episode_id,
                category="failure",
                insight=insight,
                recommendation=rec,
            )
            lessons.append(lesson)
            self._lessons_store.append(lesson)

        if successes:
            insight = f"Successfully executed {len(successes)} steps in episode '{episode_id}'"
            rec = "Cache tool responses for recurring queries to optimize execution duration."
            lesson = LessonLearned(
                lesson_id=f"lesson_{int(time.time() * 1000)}_s",
                episode_id=episode_id,
                category="success",
                insight=insight,
                recommendation=rec,
            )
            lessons.append(lesson)
            self._lessons_store.append(lesson)

        logger.info(f"[REFLECTION] Generated {len(lessons)} lessons learned for episode '{episode_id}'")
        return {
            "episode_id": episode_id,
            "final_status": final_status,
            "successes_count": len(successes),
            "failures_count": len(failures),
            "lessons_generated": [lesson.model_dump() for lesson in lessons],
        }

    def list_recommendations(self, status: str = "pending_approval") -> List[LessonLearned]:
        return [lesson for lesson in self._lessons_store if lesson.status == status]
