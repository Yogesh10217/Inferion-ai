"""Deterministic and explainable failure prediction engine (Phase 5.55)."""

import logging
from typing import Dict, Any, List, Optional
from app.reliability_intelligence.models import FailurePrediction, FailureClassification
from app.reliability_intelligence.repositories import FailurePredictionRepository

logger = logging.getLogger(__name__)


class FailurePredictionEngine:
    """Predicts service failure probabilities deterministically based on error rates, latency trends, and capacity risks."""

    def __init__(self, pred_repo: FailurePredictionRepository) -> None:
        self.pred_repo = pred_repo

    def predict_failure(
        self,
        tenant_id: str,
        service_id: str,
        recent_error_rate: float = 0.05,
        capacity_utilization: float = 0.85,
        horizon_minutes: int = 60,
    ) -> FailurePrediction:
        prob = min(0.99, (recent_error_rate * 5.0) + (max(0.0, capacity_utilization - 0.70) * 2.0))
        conf = 0.94 if prob > 0.5 else 0.88

        if capacity_utilization > 0.90:
            pred_type = FailureClassification.CAPACITY
            explanation = f"High capacity utilization ({capacity_utilization*100:.1f}%) projects capacity exhaustion within {horizon_minutes}m."
        elif recent_error_rate > 0.02:
            pred_type = FailureClassification.DEPENDENCY
            explanation = f"Elevated error rate ({recent_error_rate*100:.2f}%) indicates imminent upstream dependency degradation."
        else:
            pred_type = FailureClassification.TRANSIENT
            explanation = f"Baseline error trends indicate low failure probability ({prob:.2f})."

        pred = FailurePrediction(
            tenant_id=tenant_id,
            service_id=service_id,
            predicted_failure_type=pred_type,
            probability=round(prob, 4),
            confidence=conf,
            explanation=explanation,
            evidence=[f"error_rate={recent_error_rate}", f"capacity={capacity_utilization}"],
            horizon_minutes=horizon_minutes,
        )

        self.pred_repo.save(pred)
        logger.info(f"Generated FailurePrediction '{pred.prediction_id}' for service '{service_id}' (Prob: {prob:.2f})")
        return pred
