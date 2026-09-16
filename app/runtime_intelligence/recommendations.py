"""Runtime recommendation engine for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import List

from app.runtime_intelligence.models import RuntimeRecommendation
from app.runtime_intelligence.repositories import RuntimeRecommendationRepository

logger = logging.getLogger(__name__)


class RuntimeRecommendationEngine:
    """Formulates advisory recommendations for runtime optimization.

    Mandatory Invariant: auto_execute = False strictly enforced.
    """

    def __init__(self, repo: RuntimeRecommendationRepository) -> None:
        self.repo = repo

    def generate_recommendation(
        self, tenant_id: str, recommendation_type: str, action_description: str
    ) -> RuntimeRecommendation:
        rec = RuntimeRecommendation(
            tenant_id=tenant_id,
            recommendation_type=recommendation_type,
            action_description=action_description,
            priority="HIGH",
            auto_execute=False,  # Enforce advisory invariant
        )
        self.repo.save(rec)
        logger.info(f"Generated advisory RuntimeRecommendation '{rec.recommendation_id}' for tenant '{tenant_id}' (auto_execute=False)")
        return rec

    def list_recommendations(self, tenant_id: str) -> List[RuntimeRecommendation]:
        return self.repo.get_by_tenant(tenant_id)
