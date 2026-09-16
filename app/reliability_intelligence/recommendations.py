"""Reliability recommendation engine (Phase 5.55)."""

import logging

from app.reliability_intelligence.models import ReliabilityRecommendation

logger = logging.getLogger(__name__)


class ReliabilityRecommendationEngine:
    """Generates advisory reliability recommendations with auto_execute = False."""

    def create_recommendation(
        self, tenant_id: str, target_service: str, action_description: str, reason: str = ""
    ) -> ReliabilityRecommendation:
        rec = ReliabilityRecommendation(
            tenant_id=tenant_id,
            target_service=target_service,
            action_description=action_description,
            priority="HIGH",
            reason=reason or f"Reliability optimization for '{target_service}'",
            confidence=0.93,
            auto_execute=False,  # Mandatory invariant
        )
        logger.info(f"Generated ReliabilityRecommendation '{rec.recommendation_id}' for '{target_service}' (auto_execute=False)")
        return rec
