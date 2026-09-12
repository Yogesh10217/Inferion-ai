import pytest
from app.deployment.deployment_simulation import ProductionSimulationEngine
from app.deployment.models import PlatformReadinessClassification, RollbackTrigger


def test_rollback_simulation_without_previous_deployment():
    engine = ProductionSimulationEngine()

    evidence, rollback_res = engine.inject_failure_and_rollback(
        trigger=RollbackTrigger.CONTAINER_FAILURE,
        environment="PRODUCTION",
        deployment_mode="SIMULATION",
        previous_identity=None,  # No previous deployment exists
    )

    assert rollback_res["executed"] is False
    assert rollback_res["status"] == "ROLLBACK_PLAN_CREATED"
    assert rollback_res["execution_status"] == "ROLLBACK_EXECUTION_NOT_AVAILABLE"
    assert rollback_res["previous_deployment_reference"] == "NO_PREVIOUS_DEPLOYMENT_REFERENCE"
    assert evidence.readiness_classification == PlatformReadinessClassification.ROLLBACK_STRATEGY_READY
    assert evidence.readiness_classification != PlatformReadinessClassification.ROLLBACK_SIMULATION_VALIDATED
    assert evidence.readiness_classification != PlatformReadinessClassification.ROLLBACK_SIMULATION_EXECUTED
