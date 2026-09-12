import pytest
from app.deployment.deployment_simulation import (
    FailureInjectionPolicy,
    ProductionSimulationEngine,
)
from app.deployment.models import RollbackTrigger, PlatformReadinessClassification, DependencyStatus, DependencyCategory


def test_failure_injection_policy_gating():
    # SIMULATION and TEST modes allow failure injection
    assert FailureInjectionPolicy.can_inject("PRODUCTION", "SIMULATION") is True
    assert FailureInjectionPolicy.can_inject("TEST", "NONE") is True

    # Real PRODUCTION mode blocks failure injection
    assert FailureInjectionPolicy.can_inject("PRODUCTION", "PRODUCTION") is False
    assert FailureInjectionPolicy.can_inject("PRODUCTION", "") is False

    with pytest.raises(PermissionError):
        FailureInjectionPolicy.validate_injection_permission("PRODUCTION", "PRODUCTION")


def test_controlled_failure_injection_all_triggers():
    engine = ProductionSimulationEngine()

    triggers = [
        RollbackTrigger.CONFIGURATION_FAILURE,
        RollbackTrigger.READINESS_FAILURE,
        RollbackTrigger.HEALTH_REGRESSION,
        RollbackTrigger.DEPENDENCY_FAILURE,
        RollbackTrigger.CONTAINER_FAILURE,
        RollbackTrigger.MANAGER_REGISTRATION_FAILURE,
        RollbackTrigger.SECURITY_POLICY_VIOLATION,
        RollbackTrigger.SECRET_EXPOSURE_DETECTION,
        RollbackTrigger.DEPLOYMENT_ARTIFACT_MISMATCH,
    ]

    for trigger in triggers:
        evidence, rollback_res = engine.inject_failure_and_rollback(
            trigger=trigger,
            environment="PRODUCTION",
            deployment_mode="SIMULATION",
        )
        assert evidence.failure_trigger == trigger
        assert "FAILED" in evidence.state_transitions
        assert "ROLLBACK_REQUIRED" in evidence.state_transitions
        assert rollback_res["status"] in ("ROLLED_BACK", "ROLLBACK_PLAN_CREATED")


def test_dependency_recovery_requires_explicit_revalidation():
    # Verify stopping a dependency degrades readiness
    from app.deployment.dependency_validation import DeploymentDependencyValidator
    from app.deployment.models import EnvironmentConfig, DeploymentEnvironment

    config = EnvironmentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        application_name="Platform",
        application_version="1.0.0",
        deployment_version="5.62",
        region="us-east-1",
        instance_id="node-1",
        debug_enabled=False,
        database_url="postgresql://db:5432/db",
        cache_enabled=True,
        messaging_enabled=True,
        observability_enabled=True,
        log_level="INFO",
    )

    dep_res = DeploymentDependencyValidator.validate_all_dependencies(config)
    health_before = DeploymentDependencyValidator.evaluate_dependency_health(dep_res)
    assert health_before is True

    # Simulate Postgres failure
    for r in dep_res:
        if r.category == DependencyCategory.DATABASE or "database" in r.name.lower():
            r.status = DependencyStatus.UNAVAILABLE
            r.required = True

    health_failed = DeploymentDependencyValidator.evaluate_dependency_health(dep_res)
    assert health_failed is False

    # Simulate Postgres restoration
    for r in dep_res:
        if r.category == DependencyCategory.DATABASE or "database" in r.name.lower():
            r.status = DependencyStatus.AVAILABLE

    # Must re-evaluate explicitly
    health_restored = DeploymentDependencyValidator.evaluate_dependency_health(dep_res)
    assert health_restored is True

