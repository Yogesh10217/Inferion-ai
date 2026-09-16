"""Master reliability assessment engine (Phase 5.55)."""

import logging
from typing import Optional

from app.reliability_intelligence.models import (
    ReliabilityAssessment,
    ReliabilityLifecycleState,
    ReliabilityScore,
)
from app.reliability_intelligence.providers import ReliabilityIntelligenceProviderRegistry
from app.reliability_intelligence.repositories import ReliabilityAssessmentRepository

logger = logging.getLogger(__name__)


class MasterReliabilityEngine:
    """Evaluates cross-domain reliability scores and produces overall ReliabilityAssessment."""

    def __init__(
        self,
        provider_registry: ReliabilityIntelligenceProviderRegistry,
        rel_repo: ReliabilityAssessmentRepository,
    ) -> None:
        self.provider_registry = provider_registry
        self.rel_repo = rel_repo

    def evaluate_reliability(
        self, tenant_id: str, scope: Optional[str] = None
    ) -> ReliabilityAssessment:
        domains = self.provider_registry.list_domains()
        scores = {}
        for domain in domains:
            provider = self.provider_registry.get_provider(domain)
            if provider:
                try:
                    scores[domain] = provider.collect_assurance(tenant_id)
                except Exception as e:
                    logger.warning(f"Failed to fetch reliability score for domain '{domain}': {e}")
                    scores[domain] = 0.90

        avail_score = scores.get("operations", 0.99)
        res_score = scores.get("autonomous", 0.95)
        rec_score = scores.get("continuous", 0.94)
        dep_score = scores.get("unified", 0.92)
        cap_score = scores.get("control", 0.90)

        overall = (avail_score + res_score + rec_score + dep_score + cap_score) / 5.0

        score_obj = ReliabilityScore(
            overall_score=round(overall, 4),
            availability_score=avail_score,
            resilience_score=res_score,
            recoverability_score=rec_score,
            dependency_score=dep_score,
            capacity_score=cap_score,
        )

        assessment = ReliabilityAssessment(
            tenant_id=tenant_id,
            score=score_obj,
            state=ReliabilityLifecycleState.OBSERVING,
            findings=[{"domain": k, "score": v} for k, v in scores.items()],
        )

        self.rel_repo.save(assessment)
        logger.info(f"Generated ReliabilityAssessment '{assessment.assessment_id}' for tenant '{tenant_id}' (Score: {overall:.4f})")
        return assessment
