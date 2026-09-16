"""Failure propagation analysis engine (Phase 5.55)."""

import logging
from typing import List

from app.reliability_intelligence.models import FailurePropagationPath

logger = logging.getLogger(__name__)


class FailurePropagationEngine:
    """Analyzes failure propagation paths and blast radius without executing attacks."""

    def analyze_propagation(
        self, tenant_id: str, origin_service: str, downstream_services: List[str]
    ) -> FailurePropagationPath:
        blast_score = round(min(1.0, len(downstream_services) * 0.25), 2)
        prop_prob = 0.85 if len(downstream_services) > 2 else 0.50

        path = FailurePropagationPath(
            tenant_id=tenant_id,
            origin_service=origin_service,
            affected_nodes=downstream_services,
            propagation_probability=prop_prob,
            blast_radius_score=blast_score,
        )

        logger.info(f"Analyzed FailurePropagation from '{origin_service}' -> Blast Radius Score: {blast_score}")
        return path
