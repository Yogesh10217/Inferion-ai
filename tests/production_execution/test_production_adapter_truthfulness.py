from app.deployment.deployment_runtime_adapter import ProductionDeploymentRuntimeAdapter
from app.deployment.deployment_target import DeploymentTarget


def test_production_adapter_unconfigured_target_preserves_not_executed(monkeypatch):
    monkeypatch.delenv("PRODUCTION_KUBERNETES_CLUSTER", raising=False)
    monkeypatch.delenv("PRODUCTION_CLOUD_ENDPOINT", raising=False)

    target = DeploymentTarget(target_id="t-prod", environment="PRODUCTION", production_target=True)
    adapter = ProductionDeploymentRuntimeAdapter(target=target)

    val = adapter.validate_target()
    assert val["status"] == "NOT_AVAILABLE"
    assert val["production_deployed"] == "NOT_EXECUTED"

    deploy_res = adapter.deploy_artifact(
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        release_manifest_id="manifest-1",
    )
    assert deploy_res["status"] == "NOT_EXECUTED"
    assert deploy_res["production_deployed"] == "NOT_EXECUTED"
