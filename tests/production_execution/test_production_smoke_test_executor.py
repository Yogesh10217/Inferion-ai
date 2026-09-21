from app.deployment.deployment_runtime_adapter import SimulationDeploymentRuntimeAdapter
from app.deployment.deployment_target import DeploymentTarget
from app.deployment.models import SmokeTestExecutionStatus
from app.deployment.production_smoke_test_executor import ProductionSmokeTestExecutor


def test_smoke_test_execution_pass():
    target = DeploymentTarget(target_id="t-stg", environment="STAGING", provider="SIMULATION")
    adapter = SimulationDeploymentRuntimeAdapter(target=target)
    res = ProductionSmokeTestExecutor.execute_smoke_test_suite(adapter=adapter, explicit_smoke_test_authorized=True)

    assert res.passed is True
    assert res.status == SmokeTestExecutionStatus.PASSED
    assert len(res.passed_tests) >= 4
