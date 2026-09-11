from __future__ import annotations

import os
import pytest

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.configuration_fingerprint import ConfigurationFingerprintEngine
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.diagnostics import DeploymentDiagnosticsEngine
from app.deployment.environment import EnvironmentManager
from app.deployment.environment_isolation import EnvironmentIsolationGuard
from app.deployment.exceptions import (
    ConfigurationValidationError,
    EnvironmentIsolationError,
    SecretAccessError,
    StartupLifecycleError,
    UnsafeConfigurationError,
)
from app.deployment.health import DeploymentHealthEngine
from app.deployment.liveness import DeploymentLivenessProbe
from app.deployment.manager import DeploymentPlatformManager
from app.deployment.models import (
    DeploymentEnvironment,
    DeploymentReleaseStatus,
    DependencyStatus,
    HealthStatus,
    PlatformReadinessClassification,
    ShutdownState,
    StartupState,
)
from app.deployment.observability_configuration import DeploymentObservabilityValidator
from app.deployment.profiles import DeploymentProfile
from app.deployment.readiness import DeploymentReadinessProbe
from app.deployment.release_validation import DeploymentReleaseValidator
from app.deployment.runtime_validation import RuntimeConfigurationValidator
from app.deployment.secrets import EnvironmentSecretProvider
from app.deployment.service_registry import PlatformServiceRegistry
from app.deployment.shutdown import DeploymentShutdownManager
from app.deployment.startup import DeploymentStartupManager


def test_1_environment_selection():
    mgr = EnvironmentManager(override_env="STAGING")
    assert mgr.current_environment == DeploymentEnvironment.STAGING
    cfg = mgr.load_environment_config()
    assert cfg.environment == DeploymentEnvironment.STAGING

    with pytest.raises(ConfigurationValidationError):
        EnvironmentManager(override_env="INVALID_ENV")


def test_2_production_configuration_validation():
    os.environ["DEPLOYMENT_ENV"] = "PRODUCTION"
    os.environ["DEBUG"] = "false"
    os.environ["JWT_SECRET"] = "SuperRandomProductionSecretKey998877665544332211"
    
    mgr = EnvironmentManager()
    cfg = mgr.load_environment_config()
    res = RuntimeConfigurationValidator.validate(cfg)
    assert res.valid is True
    assert len(res.errors) == 0


def test_3_debug_rejection_in_production():
    os.environ["DEPLOYMENT_ENV"] = "PRODUCTION"
    os.environ["DEBUG"] = "true"

    mgr = EnvironmentManager()
    with pytest.raises(UnsafeConfigurationError):
        mgr.load_environment_config()


def test_4_missing_secrets_rejection():
    secret_prov = EnvironmentSecretProvider(prefix="MISSING_PFX_")
    with pytest.raises(SecretAccessError):
        secret_prov.require_secret("NON_EXISTENT_SECRET_KEY")


def test_5_configuration_fingerprint_sanitization():
    mgr = EnvironmentManager(override_env="LOCAL")
    cfg = mgr.load_environment_config()
    cfg.metadata["api_key"] = "secret_raw_key_12345"

    fp = ConfigurationFingerprintEngine.generate_fingerprint(cfg)
    assert fp.fingerprint_hash != ""
    assert "secret_raw_key_12345" not in fp.fingerprint_hash
    assert "secret_raw_key_12345" not in str(fp.sanitized_keys)


def test_6_startup_lifecycle():
    os.environ["DEPLOYMENT_ENV"] = "LOCAL"
    os.environ["DEBUG"] = "true"
    
    startup_mgr = DeploymentStartupManager()
    cfg = startup_mgr.execute_startup()
    assert startup_mgr.state == StartupState.READY
    assert cfg.environment == DeploymentEnvironment.LOCAL


def test_7_invalid_startup_transitions():
    startup_mgr = DeploymentStartupManager()
    startup_mgr.state = StartupState.INITIALIZED

    with pytest.raises(StartupLifecycleError):
        startup_mgr.transition_to(StartupState.READY)


def test_8_required_dependency_failure():
    os.environ["DEPLOYMENT_ENV"] = "STAGING"
    os.environ["DEBUG"] = "false"

    config_mgr = RuntimeConfigurationManager(EnvironmentManager(override_env="STAGING"))
    cfg = config_mgr.get_config()
    profile = DeploymentProfile.get_profile(cfg.environment)
    assert profile.require_database is True

    # Simulate failing DB dependency
    results = DeploymentDependencyValidator.validate_all_dependencies(cfg)
    results[0].status = DependencyStatus.UNAVAILABLE
    assert DeploymentDependencyValidator.evaluate_dependency_health(results) is False


def test_9_optional_dependency_degradation():
    os.environ["DEPLOYMENT_ENV"] = "LOCAL"
    config_mgr = RuntimeConfigurationManager(EnvironmentManager(override_env="LOCAL"))
    cfg = config_mgr.get_config()

    results = DeploymentDependencyValidator.validate_all_dependencies(cfg)
    # Mark optional messaging as degraded
    for r in results:
        if r.name == "EventBus/Broker":
            r.status = DependencyStatus.DEGRADED
    assert DeploymentDependencyValidator.evaluate_dependency_health(results) is True


def test_10_health_endpoint():
    mgr = DeploymentPlatformManager(environment_override="LOCAL")
    report = mgr.check_health()
    assert report.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)
    assert len(report.checks) >= 4


def test_11_readiness_endpoint():
    mgr = DeploymentPlatformManager(environment_override="LOCAL")
    res = mgr.check_readiness()
    assert res["status"] in ("READY", "NOT_READY")
    assert "checks" in res


def test_12_liveness_endpoint():
    res = DeploymentLivenessProbe.check_liveness()
    assert res["live"] is True
    assert res["status"] == "HEALTHY"


def test_13_diagnostics_sanitization():
    mgr = DeploymentPlatformManager(environment_override="LOCAL")
    diag = mgr.get_diagnostics()
    assert diag.application_name == "Enterprise-AI-Platform"
    assert "password" not in str(diag)


def test_14_graceful_shutdown():
    os.environ["DEPLOYMENT_ENV"] = "LOCAL"
    shutdown_mgr = DeploymentShutdownManager()
    state = shutdown_mgr.execute_shutdown()
    assert state == ShutdownState.STOPPED


def test_15_manager_validation():
    container = ServiceContainer()
    status = PlatformServiceRegistry.validate_platform_managers(container)
    assert "unified_intelligence_manager" in status
    assert status["unified_intelligence_manager"] is True
    assert len(PlatformServiceRegistry.get_registered_manager_names(container)) == 9


def test_16_observability_validation():
    config_mgr = RuntimeConfigurationManager(EnvironmentManager(override_env="LOCAL"))
    cfg = config_mgr.get_config()
    obs_res = DeploymentObservabilityValidator.validate_observability(cfg)
    assert "status" in obs_res
    assert obs_res["metrics_active"] is True


def test_17_release_validation():
    os.environ["DEPLOYMENT_ENV"] = "LOCAL"
    validator = DeploymentReleaseValidator()
    res = validator.validate_release_readiness()
    assert res.status in (DeploymentReleaseStatus.READY, DeploymentReleaseStatus.CONDITIONALLY_READY)


def test_18_secret_provider():
    os.environ["TEST_DEPLOYMENT_SECRET"] = "super_secret_val"
    prov = EnvironmentSecretProvider()
    assert prov.get_secret("TEST_DEPLOYMENT_SECRET") == "super_secret_val"
    assert prov.require_secret("TEST_DEPLOYMENT_SECRET") == "super_secret_val"


def test_19_cross_environment_isolation():
    os.environ["DEPLOYMENT_ENV"] = "STAGING"
    mgr = EnvironmentManager()
    cfg = mgr.load_environment_config()

    with pytest.raises(EnvironmentIsolationError):
        EnvironmentIsolationGuard.enforce_environment_match(cfg, DeploymentEnvironment.PRODUCTION)


def test_20_full_deployment_lifecycle():
    os.environ["DEPLOYMENT_ENV"] = "LOCAL"
    mgr = DeploymentPlatformManager(environment_override="LOCAL")
    
    config = mgr.startup()
    assert config.environment == DeploymentEnvironment.LOCAL
    
    health = mgr.check_health()
    assert health.status != HealthStatus.UNHEALTHY
    
    readiness = mgr.check_readiness()
    assert readiness["ready"] is True
    
    shutdown = mgr.shutdown()
    assert shutdown == ShutdownState.STOPPED
