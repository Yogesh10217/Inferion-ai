"""Saturation prediction engine for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import SaturationAssessment

logger = logging.getLogger(__name__)


class SaturationPredictionEngine:
    """Predicts resource exhaustion timelines and capacity breach probabilities."""

    def predict_saturation(
        self, tenant_id: str, resource_id: str, current_utilization_pct: float = 75.0
    ) -> SaturationAssessment:
        is_saturated = current_utilization_pct >= 85.0
        prob = min(1.0, current_utilization_pct / 90.0)
        time_to_sat = max(0.0, (100.0 - current_utilization_pct) * 2.5)

        sat = SaturationAssessment(
            tenant_id=tenant_id,
            resource_id=resource_id,
            is_saturated=is_saturated,
            saturation_probability=round(prob, 4),
            time_to_saturation_hours=round(time_to_sat, 1),
        )
        logger.info(f"Evaluated SaturationAssessment for resource '{resource_id}': Saturated={is_saturated}, Prob={prob:.2f}")
        return sat


SaturationEngine = SaturationPredictionEngine
