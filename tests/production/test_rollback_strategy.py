from app.deployment.models import DeploymentIdentity, PlatformReadinessClassification, RollbackTrigger
from app.deployment.rollback import RollbackStrategyEngine


def test_rollback_plan_generated_for_all_triggers():
    identity = DeploymentIdentity(
        application_version="1.0.0",
        deployment_version="5.61.0",
        build_identifier="b101",
        git_revision="git-commit-hash",
        environment="PRODUCTION",
    )

    for trigger in RollbackTrigger:
        plan = RollbackStrategyEngine.generate_rollback_plan(trigger=trigger, deployment_identity=identity)
        assert plan.trigger == trigger
        assert len(plan.required_operator_actions) > 0
        assert len(plan.automatic_actions) > 0
        assert plan.safety_classification == PlatformReadinessClassification.ROLLBACK_STRATEGY_READY
        assert plan.previous_deployment_reference == "NO_PREVIOUS_DEPLOYMENT_REFERENCE"


def test_rollback_plan_with_explicit_previous_reference():
    identity = DeploymentIdentity(
        application_version="1.0.0",
        deployment_version="5.61.0",
        build_identifier="b101",
        git_revision="git-commit-hash",
        environment="PRODUCTION",
    )

    plan = RollbackStrategyEngine.generate_rollback_plan(
        trigger=RollbackTrigger.HEALTH_REGRESSION,
        deployment_identity=identity,
        previous_deployment_reference="enterprise-ai-platform:5.60.0",
    )
    assert plan.previous_deployment_reference == "enterprise-ai-platform:5.60.0"


def test_rollback_state_initialization():
    identity = DeploymentIdentity(
        application_version="1.0.0",
        deployment_version="5.61.0",
        build_identifier="b101",
        git_revision="git-commit-hash",
        environment="PRODUCTION",
    )

    state = RollbackStrategyEngine.initialize_rollback_state(
        trigger=RollbackTrigger.SECRET_EXPOSURE_DETECTION,
        deployment_identity=identity,
    )
    assert state.status == "ROLLBACK_STRATEGY_READY"
    assert not state.executed
    assert state.active_plan is not None
    assert state.active_plan.trigger == RollbackTrigger.SECRET_EXPOSURE_DETECTION
