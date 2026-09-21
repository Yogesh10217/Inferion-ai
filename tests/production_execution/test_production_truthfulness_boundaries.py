from app.deployment.deployment_authorization import DeploymentAuthorizationEngine
from app.deployment.deployment_target import DeploymentTarget
from app.deployment.models import ProductionDeploymentState
from app.deployment.production_deployment_executor import ProductionDeploymentExecutor


def test_unconfigured_production_target_preserves_not_executed(monkeypatch):
    monkeypatch.delenv("PRODUCTION_KUBERNETES_CLUSTER", raising=False)
    monkeypatch.delenv("PRODUCTION_CLOUD_ENDPOINT", raising=False)

    target = DeploymentTarget(target_id="t-prod", environment="PRODUCTION", production_target=True)

    auth = DeploymentAuthorizationEngine.create_authorization_request(
        release_candidate_id="rc-1",
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        git_revision="rev-1",
        environment="PRODUCTION",
    )
    for cat in ["TECHNICAL", "SECURITY", "DATABASE", "OPERATIONS", "RELEASE", "DEPLOYMENT_EXECUTOR"]:
        DeploymentAuthorizationEngine.grant_category_approval(
            auth, cat, "admin", "sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff", "rev-1"
        )

    executor = ProductionDeploymentExecutor()
    res = executor.execute(
        authorization_record=auth,
        target=target,
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        git_revision="rev-1",
    )

    assert res.state == ProductionDeploymentState.FAILED
    assert any("PRODUCTION_RUNTIME_TARGET_NOT_AVAILABLE" in err for err in res.blocking_reasons)
    assert res.certification is not None
    assert res.certification.truthfulness_status == "NOT_EXECUTED"
