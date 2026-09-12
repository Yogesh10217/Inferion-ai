import pytest
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.models import DeploymentDecision, DeploymentReleaseStatus, PlatformReadinessClassification
from app.deployment.release_validation import DeploymentReleaseValidator


def test_production_release_gate_allow_path(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_app_user:prod_secure_db_pass_9988@prod-db:5432/app")
    monkeypatch.setenv("REDIS_URL", "redis://prod-redis:6379")
    monkeypatch.setenv("JWT_SECRET", "valid-complex-production-secret-999")
    monkeypatch.setenv("IMAGE_TAG", "enterprise-ai-platform:5.61.0")


    config_mgr = RuntimeConfigurationManager()
    validator = DeploymentReleaseValidator(config_manager=config_mgr)
    res = validator.validate_release_readiness()

    assert res.status == DeploymentReleaseStatus.READY
    assert res.decision == DeploymentDecision.ALLOW
    assert res.readiness_classification == PlatformReadinessClassification.PRODUCTION_SAFETY_VALIDATED
    assert "debug_mode_safe" in res.passed_checks
    assert "secret_canary_audit_passed" in res.passed_checks
    assert "rollback_strategy_available" in res.passed_checks


def test_production_release_gate_block_on_debug(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_app_user:prod_secure_db_pass_9988@prod-db:5432/app")
    monkeypatch.setenv("REDIS_URL", "redis://prod-redis:6379")
    monkeypatch.setenv("JWT_SECRET", "valid-complex-production-secret-999")

    config_mgr = RuntimeConfigurationManager()
    validator = DeploymentReleaseValidator(config_manager=config_mgr)
    res = validator.validate_release_readiness()

    assert res.status == DeploymentReleaseStatus.BLOCKED
    assert res.decision in (DeploymentDecision.BLOCK, DeploymentDecision.ROLLBACK_REQUIRED)
    assert len(res.blocking_reasons) > 0


def test_production_release_gate_rollback_required_on_secret_canary(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_app_user:prod_secure_db_pass_9988@prod-db:5432/app")
    monkeypatch.setenv("REDIS_URL", "redis://prod-redis:6379")
    monkeypatch.setenv("JWT_SECRET", "password123")


    config_mgr = RuntimeConfigurationManager()
    validator = DeploymentReleaseValidator(config_manager=config_mgr)
    res = validator.validate_release_readiness()

    assert res.status == DeploymentReleaseStatus.BLOCKED
    assert res.decision == DeploymentDecision.ROLLBACK_REQUIRED
    assert res.readiness_classification == PlatformReadinessClassification.ROLLBACK_STRATEGY_READY


def test_truthfulness_boundary_contract(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_app_user:prod_secure_db_pass_9988@prod-db:5432/app")
    monkeypatch.setenv("REDIS_URL", "redis://prod-redis:6379")
    monkeypatch.setenv("JWT_SECRET", "valid-complex-production-secret-999")

    config_mgr = RuntimeConfigurationManager()
    validator = DeploymentReleaseValidator(config_manager=config_mgr)
    res = validator.validate_release_readiness()

    # In Phase 5.61, live production deployment and execution are NOT executed.
    assert res.readiness_classification != PlatformReadinessClassification.PRODUCTION_READY
    assert res.decision != DeploymentDecision.NOT_EXECUTED or res.decision == DeploymentDecision.ALLOW
