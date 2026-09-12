import os
import pytest
from app.deployment.environment import EnvironmentManager
from app.deployment.exceptions import ConfigurationValidationError, UnsafeConfigurationError
from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


def test_production_debug_rejected(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "valid-complex-production-secret-999")
    
    mgr = EnvironmentManager()
    with pytest.raises(UnsafeConfigurationError) as exc_info:
        mgr.load_environment_config()
    assert "ENVIRONMENT_POLICY_VIOLATION" in str(exc_info.value) or "debug_enabled=True" in str(exc_info.value)


def test_production_sqlite_rejected(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./app.db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "valid-complex-production-secret-999")

    mgr = EnvironmentManager()
    with pytest.raises(UnsafeConfigurationError) as exc_info:
        mgr.load_environment_config()
    assert "SQLite" in str(exc_info.value)


def test_production_missing_database_url_rejected(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "valid-complex-production-secret-999")

    mgr = EnvironmentManager()
    # If empty database URL
    cfg = EnvironmentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        application_name="TestApp",
        application_version="1.0.0",
        deployment_version="5.61.0",
        region="us-east-1",
        instance_id="inst-1",
        debug_enabled=False,
        database_url="",
        cache_enabled=True,
        messaging_enabled=False,
        observability_enabled=True,
        log_level="INFO",
    )
    with pytest.raises(ConfigurationValidationError):
        mgr.validate_environment_safety(cfg)


def test_empty_deployment_version_rejected(monkeypatch):
    mgr = EnvironmentManager(override_env="PRODUCTION")
    cfg = EnvironmentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        application_name="TestApp",
        application_version="1.0.0",
        deployment_version="",
        region="us-east-1",
        instance_id="inst-1",
        debug_enabled=False,
        database_url="postgresql+asyncpg://user:pass@localhost:5432/db",
        cache_enabled=False,
        messaging_enabled=False,
        observability_enabled=True,
        log_level="INFO",
    )
    with pytest.raises(ConfigurationValidationError):
        mgr.validate_environment_safety(cfg)
