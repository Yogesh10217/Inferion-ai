"""
Tests for Evidence Level Boundaries and Mapping.
"""

from app.reliability.chaos_engine import ChaosEngineeringEngine, ChaosExperiment
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel
from app.reliability.reliability_models import ChaosExecutionMode, ChaosFailureType


def test_evidence_level_mapping_from_chaos_execution_mode():
    engine = ChaosEngineeringEngine()

    exp_sim = ChaosExperiment("e1", "Sim", "target", ChaosFailureType.APPLICATION_CRASH, ChaosExecutionMode.SIMULATION)
    res_sim = engine.run_chaos_experiment(exp_sim)
    assert res_sim.evidence_level == ReliabilityEvidenceLevel.SIMULATION_RUNTIME

    exp_cnt = ChaosExperiment(
        "e2", "Container", "target", ChaosFailureType.CONTAINER_RESTART, ChaosExecutionMode.CONTAINER
    )
    res_cnt = engine.run_chaos_experiment(exp_cnt)
    assert res_cnt.evidence_level == ReliabilityEvidenceLevel.CONTAINER_RUNTIME
