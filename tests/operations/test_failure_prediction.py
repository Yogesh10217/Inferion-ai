"""Unit tests for FailurePredictionEngine."""

import pytest
from app.operations.prediction import FailurePredictionEngine, PredictionRiskLevel


def test_capacity_risk_prediction():
    engine = FailurePredictionEngine()

    # Queue depth 90 / 100 -> HIGH risk prediction
    pred = engine.predict_capacity_risk("t_pred", "worker_pool_1", current_queue_depth=90, max_capacity=100)

    assert pred is not None
    assert pred.risk_level == PredictionRiskLevel.HIGH
    assert pred.predictive_signal == "QUEUE_GROWTH"
    assert pred.recommended_action == "SCALE_WORKER_POOL"
