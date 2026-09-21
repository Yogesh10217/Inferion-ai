from app.deployment.deployment_target import DeploymentTarget
from app.deployment.models import DeploymentTargetStatus


def test_deployment_target_staging_validation():
    target = DeploymentTarget(target_id="t-stg", environment="STAGING", endpoint="http://localhost:8003")
    res = target.validate_target()
    assert res["status"] == "VALIDATED"
    assert target.runtime_status == DeploymentTargetStatus.TARGET_CONNECTIVITY_VALIDATED


def test_deployment_target_production_unconfigured_validation(monkeypatch):
    monkeypatch.delenv("PRODUCTION_KUBERNETES_CLUSTER", raising=False)
    monkeypatch.delenv("PRODUCTION_CLOUD_ENDPOINT", raising=False)

    target = DeploymentTarget(target_id="t-prod", environment="PRODUCTION", production_target=True)
    res = target.validate_target()
    assert res["status"] == "NOT_AVAILABLE"
    assert target.runtime_status == DeploymentTargetStatus.TARGET_NOT_AVAILABLE
