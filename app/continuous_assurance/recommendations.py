"""Continuous assurance recommendation engine (Phase 5.54)."""

import logging
from typing import Dict, Any, List
from app.continuous_assurance.models import AdaptiveControlRecommendation
from app.continuous_assurance.repositories import RecommendationRepository

logger = logging.getLogger(__name__)


class ContinuousAssuranceRecommendationEngine:
    """Generates continuous assurance recommendations with advisory auto_execute = False."""

    def __init__(self, rec_repo: RecommendationRepository) -> None:
        self.rec_repo = rec_repo

    def create_recommendation(
        self, tenant_id: str, target_control: str, action_description: str, reason: str = ""
    ) -> AdaptiveControlRecommendation:
        rec = AdaptiveControlRecommendation(
            tenant_id=tenant_id,
            target_control=target_control,
            action_description=action_description,
            priority="HIGH",
            reason=reason or f"Recommendation for '{target_control}'",
            confidence=0.94,
            auto_execute=False,  # Strict invariant
        )
        self.rec_repo.save(rec)
        return rec

    def list_recommendations(self, tenant_id: str) -> List[AdaptiveControlRecommendation]:
        return self.rec_repo.list_by_tenant(tenant_id)
