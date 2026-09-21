"""Unit tests for ProductionSettings and ConfigurationValidator."""

import pytest

from app.config.production_settings import ConfigurationValidator, EnvironmentName, ProductionSettings
from app.security.exceptions import SecurityPolicyViolation


def test_production_config_validation_pass():
    settings = ProductionSettings(
        environment=EnvironmentName.PRODUCTION,
        jwt_secret="a-very-secure-32-byte-long-production-jwt-secret",
        database_url="postgresql+asyncpg://user:pass@host:5432/db",
    )
    res = ConfigurationValidator.validate_production_configuration(settings)
    assert res["valid"] is True


def test_production_config_validation_failure():
    settings = ProductionSettings(
        environment=EnvironmentName.PRODUCTION,
        jwt_secret="super-secret-key-change-in-production",
    )
    with pytest.raises(SecurityPolicyViolation):
        ConfigurationValidator.validate_production_configuration(settings)
