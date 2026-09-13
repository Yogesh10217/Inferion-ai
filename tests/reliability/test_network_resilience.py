"""
Tests for Network Resilience Evaluator Module.
"""

from app.reliability.network_resilience import NetworkResilienceEvaluator


def test_network_resilience_partition_simulation():
    evaluator = NetworkResilienceEvaluator()
    res = evaluator.evaluate_network_resilience(simulated_latency_ms=100.0, simulated_partition=True)
    assert res.latency_tolerated is True
    assert res.partition_handled is True
