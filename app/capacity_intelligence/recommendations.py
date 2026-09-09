"""Capacity recommendation engine for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import List
from app.capacity_intelligence.models import CapacityRecommendation
from app.capacity_intelligence.repositories import RecommendationRepository

logger = logging.getLogger(__name__)


class CapacityRecommendationEngine:
    """Formulates advisory capacity recommendations.

    Mandatory Invariant: auto_execute = False strictly enforced.
    """

    def __init__(self, repo: RecommendationRepository) -> None:
        self.repo = repo

    def generate_recommendation(
        self, tenant_id: str, target_resource_id: str, recommendation_type: str, action_description: str
    ) -> CapacityRecommendation:
        rec = CapacityRecommendation(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            recommendation_type=recommendation_type,
            action_description=action_description,
            priority="HIGH",
            auto_execute=False,  # Enforce advisory invariant
        )
        self.repo.save(rec)
        logger.info(f"Generated advisory CapacityRecommendation '{rec.recommendation_id}' for resource '{target_resource_id}' (auto_execute=False)")
        return rec

    def list_recommendations(self, tenant_id: str) -> List[CapacityRecommendation]:
        return self.repo.get_by_tenant(tenant_id)
