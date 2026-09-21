from app.deployment.deployment_metadata import DeploymentIdentityBuilder
from app.deployment.environment import EnvironmentManager
from app.deployment.models import RollbackTrigger
from app.deployment.rollback import RollbackStrategyEngine


def test_rollback_strategy_generation():
    cfg = EnvironmentManager().load_environment_config()
    identity = DeploymentIdentityBuilder.build_identity(cfg)
    plan = RollbackStrategyEngine.generate_rollback_plan(
        trigger=RollbackTrigger.DEPLOYMENT_ARTIFACT_MISMATCH, deployment_identity=identity
    )

    assert plan.trigger == RollbackTrigger.DEPLOYMENT_ARTIFACT_MISMATCH
    assert plan.deployment_identity.deployment_version == identity.deployment_version
