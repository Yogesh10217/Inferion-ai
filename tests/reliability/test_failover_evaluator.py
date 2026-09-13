"""
Tests for Failover Evaluator Module.
"""

from app.reliability.failover_evaluator import FailoverEvaluationStatus, FailoverEvaluator


def test_failover_evaluator_simulation_validated():
    evaluator = FailoverEvaluator()
    res = evaluator.evaluate_failover_readiness(real_production_executed=False)
    assert res.status == FailoverEvaluationStatus.FAILOVER_SIMULATION_VALIDATED
    assert res.production_failover_executed is False
