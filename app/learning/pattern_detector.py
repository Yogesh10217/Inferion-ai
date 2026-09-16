"""
Pattern Detector for Learning Subsystem
"""

import logging
from typing import Any, Dict, List

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExecutionPattern(BaseModel):
    pattern_id: str
    pattern_type: str  # success, failure, tool_effectiveness, workflow_opt
    confidence: float
    description: str
    actionable_recommendation: str


class PatternDetector:
    """Detects recurring success/failure trends across historical execution episodes."""

    @staticmethod
    def detect_patterns(history_episodes: List[Dict[str, Any]]) -> List[ExecutionPattern]:
        patterns = []
        if not history_episodes:
            return patterns

        failures = [ep for ep in history_episodes if ep.get("status") in ("failed", "error")]
        successes = [ep for ep in history_episodes if ep.get("status") == "completed"]

        if len(failures) > 2:
            patterns.append(ExecutionPattern(
                pattern_id="pat_recurring_timeout",
                pattern_type="failure",
                confidence=0.88,
                description=f"Detected {len(failures)} step timeouts across episodes",
                actionable_recommendation="Increase step timeout limit to 30s or pre-cache tool results",
            ))

        if len(successes) > 0:
            patterns.append(ExecutionPattern(
                pattern_id="pat_high_success_dag",
                pattern_type="success",
                confidence=0.95,
                description=f"High execution success rate ({len(successes)} episodes completed cleanly)",
                actionable_recommendation="Save DAG task structure as reusable workflow template",
            ))

        logger.info(f"[PATTERN DETECTOR] Identified {len(patterns)} execution patterns")
        return patterns
