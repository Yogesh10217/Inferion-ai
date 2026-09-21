from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.models import DeploymentDecision, DeploymentReleaseStatus
from app.deployment.release_validation import DeploymentReleaseValidator
from app.deployment.service_registry import PlatformServiceRegistry


def test_service_container_9_manager_invariant():
    container = ServiceContainer()
    manager_status = PlatformServiceRegistry.validate_platform_managers(container)
    assert len(manager_status) == 9
    assert all(manager_status.values()), f"Platform managers incomplete: {manager_status}"


def test_observability_required_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("OBSERVABILITY_ENABLED", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_app_user:prod_secure_db_pass_9988@prod-db:5432/app")
    monkeypatch.setenv("REDIS_URL", "redis://prod-redis:6379")
    monkeypatch.setenv("JWT_SECRET", "valid-complex-production-secret-999")

    config_mgr = RuntimeConfigurationManager()
    validator = DeploymentReleaseValidator(config_manager=config_mgr)
    res = validator.validate_release_readiness()

    assert "observability_unconfigured" in res.failed_checks
    assert res.status == DeploymentReleaseStatus.BLOCKED
    assert res.decision == DeploymentDecision.BLOCK


def test_production_missing_observability_blocks_release(monkeypatch):
    test_observability_required_in_production(monkeypatch)
