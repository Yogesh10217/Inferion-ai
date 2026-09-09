"""Demand prediction engine for Capacity Intelligence (Phase 5.56)."""

import logging
from app.capacity_intelligence.models import DemandPrediction

logger = logging.getLogger(__name__)


class DemandPredictionEngine:
    """Predicts workload, compute, inference, and request growth demand."""

    def predict_demand(
        self, tenant_id: str, service_id: str, current_qps: float = 200.0, growth_pct: float = 25.0
    ) -> DemandPrediction:
        predicted_qps = current_qps * (1.0 + (growth_pct / 100.0))
        pred = DemandPrediction(
            tenant_id=tenant_id,
            service_id=service_id,
            expected_qps_growth=growth_pct,
            predicted_demand_units=round(predicted_qps, 2),
        )
        logger.info(f"Generated DemandPrediction for service '{service_id}': Predicted Demand={predicted_qps:.2f} QPS")
        return pred
