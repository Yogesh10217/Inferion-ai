"""
Tests for Cache Resilience Evaluator Module.
"""

from app.reliability.cache_resilience import CacheResilienceEvaluator


def test_cache_resilience_fallback():
    evaluator = CacheResilienceEvaluator()
    res = evaluator.evaluate_cache_resilience(cache_available=False, fallback_behavior_ready=True)
    assert res.details.get("fallback_active") is True
    assert res.resilience_score < 100.0
