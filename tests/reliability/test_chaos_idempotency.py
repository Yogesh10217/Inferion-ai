"""
Tests for Chaos Experiment Idempotency.
"""

from app.reliability.chaos_engine import ChaosEngineeringEngine, ChaosExperiment
from app.reliability.reliability_models import ChaosExecutionMode, ChaosFailureType


def test_chaos_experiment_idempotency():
    engine = ChaosEngineeringEngine()
    exp = ChaosExperiment(
        experiment_id="exp-idemp-101",
        name="Idempotent Test",
        target="redis_service",
        failure_type=ChaosFailureType.CACHE_UNAVAILABLE,
        execution_mode=ChaosExecutionMode.SIMULATION,
    )

    res1 = engine.run_chaos_experiment(exp)
    assert res1.idempotent_replay is False

    # Second execution with duplicate experiment_id returns existing result with idempotent_replay=True
    res2 = engine.run_chaos_experiment(exp)
    assert res2.idempotent_replay is True
    assert res2.fingerprint == res1.fingerprint
