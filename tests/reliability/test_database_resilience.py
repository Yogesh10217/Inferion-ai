"""
Tests for Database Resilience Evaluator Module.
"""

from app.reliability.database_resilience import DatabaseResilienceEvaluator


def test_database_resilience_simulation_status():
    evaluator = DatabaseResilienceEvaluator()
    res = evaluator.evaluate_database_resilience(real_production_executed=False)
    assert res.simulation_status == "DATABASE_RECOVERY_SIMULATION_VALIDATED"
    assert res.production_database_recovery_executed is False
    assert res.resilience_score == 100.0
