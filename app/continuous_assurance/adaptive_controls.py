"""Adaptive control recommendation engine (Phase 5.54)."""

import logging

from app.continuous_assurance.models import AdaptiveControlRecommendation
from app.continuous_assurance.repositories import RecommendationRepository

logger = logging.getLogger(__name__)


class AdaptiveControlEngine:
    """Generates advisory adaptive control recommendations with mandatory auto_execute = False."""

    def __init__(self, rec_repo: RecommendationRepository) -> None:
        self.rec_repo = rec_repo

    def recommend_adaptive_control(
        self, tenant_id: str, target_control: str, action_description: str, priority: str = "HIGH"
    ) -> AdaptiveControlRecommendation:
        rec = AdaptiveControlRecommendation(
            tenant_id=tenant_id,
            target_control=target_control,
            action_description=action_description,
            priority=priority,
            reason=f"Adaptive assurance recommendation for '{target_control}'",
            confidence=0.92,
            auto_execute=False,  # Enforce strict invariant
        )

        self.rec_repo.save(rec)
        logger.info(f"Generated AdaptiveControlRecommendation '{rec.recommendation_id}' for control '{target_control}' (auto_execute=False)")
        return rec
