"""Closed-loop assurance feedback engine (Phase 5.54)."""

import logging
from typing import Any, Dict

from app.continuous_assurance.feedback_loop_control import FeedbackLoopController

logger = logging.getLogger(__name__)


class ContinuousAssuranceFeedbackEngine:
    """Coordinates the closed-loop feedback lifecycle from Observation to Verification."""

    def __init__(self, loop_controller: FeedbackLoopController) -> None:
        self.loop_controller = loop_controller

    def process_feedback_cycle(self, tenant_id: str, cycle_key: str) -> Dict[str, Any]:
        iteration = self.loop_controller.track_iteration(f"{tenant_id}:{cycle_key}")
        logger.info(f"Executed feedback cycle iteration {iteration} for tenant '{tenant_id}' (key: {cycle_key})")
        return {
            "tenant_id": tenant_id,
            "cycle_key": cycle_key,
            "iteration": iteration,
            "status": "FEEDBACK_PROCESSED",
        }
