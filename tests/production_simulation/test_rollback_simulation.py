import pytest
from app.deployment.deployment_simulation import ProductionSimulationEngine
from app.deployment.models import DeploymentIdentity, PlatformReadinessClassification, RollbackTrigger
from app.deployment.rollback import RollbackStrategyEngine


def test_rollback_simulation_execution_with_previous_deployment():
    engine = ProductionSimulationEngine()

    prev_identity = DeploymentIdentity(
        application_version="1.0.0",
        deployment_version="5.61",
        build_identifier="build-5.61",
        git_revision="git-561",
        environment="PRODUCTION",
        image_tag="enterprise-ai-platform:5.61",
        image_digest="sha256:8888888888888888888888888888888888888888aaaabbbbccccddddeeeeffff",
    )

    evidence, rollback_res = engine.inject_failure_and_rollback(
        trigger=RollbackTrigger.HEALTH_REGRESSION,
        environment="PRODUCTION",
        deployment_mode="SIMULATION",
        previous_identity=prev_identity,
    )

    assert rollback_res["executed"] is True
    assert rollback_res["status"] == "ROLLED_BACK"
    assert rollback_res["execution_status"] == "VALIDATED"
    assert rollback_res["restored_identity"].deployment_version == "5.61"
    assert rollback_res["restored_image_digest"] == prev_identity.image_digest
    assert rollback_res["registered_manager_count"] == 9
    assert evidence.readiness_classification == PlatformReadinessClassification.ROLLBACK_SIMULATION_VALIDATED
