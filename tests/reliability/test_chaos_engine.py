"""
Tests for Chaos Engineering Engine Module.
"""

from app.reliability.reliability_models import ChaosExecutionMode, ChaosFailureType
from app.reliability.chaos_engine import ChaosEngineeringEngine, ChaosExperiment
from app.reliability.chaos_state_machine import ChaosState


def test_chaos_engine_experiment_lifecycle():
    engine = ChaosEngineeringEngine()
    exp = ChaosExperiment(
        experiment_id="exp-life-1",
        name="App Crash",
        target="app_service",
        failure_type=ChaosFailureType.APPLICATION_CRASH,
        execution_mode=ChaosExecutionMode.SIMULATION,
    )

    res = engine.run_chaos_experiment(exp)
    assert res.status == ChaosState.COMPLETED
    assert res.fingerprint.startswith("sha256:")
