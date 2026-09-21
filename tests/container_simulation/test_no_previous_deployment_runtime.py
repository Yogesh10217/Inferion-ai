from app.deployment.deployment_simulation import ProductionSimulationEngine
from app.deployment.models import RollbackTrigger


def test_no_previous_deployment_reference_contract():
    engine = ProductionSimulationEngine()
    evidence, rollback_res = engine.inject_failure_and_rollback(
        trigger=RollbackTrigger.HEALTH_REGRESSION,
        environment="PRODUCTION",
        deployment_mode="SIMULATION",
        previous_identity=None,
    )

    assert rollback_res["executed"] is False
    assert rollback_res["status"] in ("NO_PREVIOUS_DEPLOYMENT_REFERENCE", "ROLLBACK_PLAN_CREATED")
    assert rollback_res["execution_status"] == "ROLLBACK_EXECUTION_NOT_AVAILABLE"
    assert rollback_res["previous_deployment_reference"] == "NO_PREVIOUS_DEPLOYMENT_REFERENCE"
