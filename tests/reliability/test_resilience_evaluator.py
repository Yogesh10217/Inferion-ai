"""
Tests for Resilience Evaluator Module.
"""

from app.reliability.reliability_models import ReliabilityStatus
from app.reliability.resilience_evaluator import ResilienceEvaluator


def test_resilience_evaluator_scoring():
    evaluator = ResilienceEvaluator()
    res = evaluator.evaluate_resilience()
    assert res.resilience_score == 100.0
    assert res.status == ReliabilityStatus.HEALTHY


def test_resilience_evaluator_degraded():
    evaluator = ResilienceEvaluator()
    res = evaluator.evaluate_resilience(
        database_resilience=40.0,
        cache_resilience=40.0,
        network_resilience=40.0,
    )
    assert res.resilience_score < 90.0
    assert res.status == ReliabilityStatus.DEGRADED
