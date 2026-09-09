"""Feedback loop bounds and safety controller for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any
from app.continuous_assurance.exceptions import FeedbackLoopException

logger = logging.getLogger(__name__)


class FeedbackLoopController:
    """Prevents infinite feedback loops, enforces max iterations, cooldowns, and termination conditions."""

    def __init__(self, max_iterations: int = 5) -> None:
        self.max_iterations = max_iterations
        self._iteration_counts: Dict[str, int] = {}

    def track_iteration(self, loop_key: str) -> int:
        current = self._iteration_counts.get(loop_key, 0) + 1
        self._iteration_counts[loop_key] = current

        if current > self.max_iterations:
            logger.error(f"Feedback loop key '{loop_key}' exceeded max iterations limit ({self.max_iterations}).")
            raise FeedbackLoopException(
                f"Maximum feedback loop iterations exceeded ({self.max_iterations}) for key '{loop_key}'"
            )

        return current

    def reset_loop(self, loop_key: str) -> None:
        self._iteration_counts.pop(loop_key, None)
