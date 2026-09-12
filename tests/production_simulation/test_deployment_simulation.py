import pytest
from app.deployment.deployment_simulation import (
    ProductionSimulationEngine,
    EvidenceExecutionStatus,
    ExecutionCategory,
)
from app.deployment.models import PlatformReadinessClassification


def test_production_simulation_engine_run_success():
    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation(
        environment="PRODUCTION",
        deployment_mode="SIMULATION",
        image_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
    )

    assert evidence.execution_status == EvidenceExecutionStatus.VALIDATED
    assert evidence.readiness_classification == PlatformReadinessClassification.PRODUCTION_SIMULATION_VALIDATED
    assert evidence.execution_category == ExecutionCategory.HTTP_RUNTIME
    assert "VALIDATED" in evidence.state_transitions
    assert evidence.probe_results["live"]["status_code"] == 200
    assert evidence.probe_results["ready"]["ready"] is True
    assert evidence.security_results["docs_disabled"] is True


def test_production_simulation_engine_run_digest_mismatch():
    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation(
        environment="PRODUCTION",
        deployment_mode="SIMULATION",
        image_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        runtime_digest="sha256:9999999999999999999999999999999999999999aaaabbbbccccddddeeeeffff",
    )

    assert evidence.execution_status == EvidenceExecutionStatus.FAILED
    assert evidence.readiness_classification == PlatformReadinessClassification.RUNTIME_BLOCKED
    assert "FAILED" in evidence.state_transitions
    assert "BLOCKED" in evidence.state_transitions
