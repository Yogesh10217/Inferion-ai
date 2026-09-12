import os
import pytest
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.environment import EnvironmentManager
from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


def test_production_simulation_container_configuration():
    res = ContainerValidationEngine.validate_container_environment(
        image_tag="enterprise-ai-platform:5.62", is_production=True
    )

    assert res["dockerfile_present"] is True
    assert res["dockerignore_present"] is True
    assert res["non_root_user"] is True
    assert res["image_tag_valid"] is True


def test_production_simulation_environment_flags(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEPLOYMENT_MODE", "SIMULATION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://app_user:app_pass_prod_sim@simulation-db:5432/llm_engine_sim")
    monkeypatch.setenv("JWT_SECRET", "PROD_SIMULATION_SECURE_JWT_SECRET_HASH_5_62")

    mgr = EnvironmentManager()
    config = mgr.load_environment_config()
    assert config.environment == DeploymentEnvironment.PRODUCTION
    assert config.debug_enabled is False
    assert config.is_production() is True



