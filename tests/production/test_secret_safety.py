import pytest

from app.deployment.environment import EnvironmentManager
from app.deployment.exceptions import UnsafeConfigurationError
from app.deployment.secrets import EnvironmentSecretProvider, SecretsSanitizer


def test_unsafe_fallback_secret_rejected_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "super-secret-key-change-in-production")

    mgr = EnvironmentManager()
    with pytest.raises(UnsafeConfigurationError) as exc_info:
        mgr.load_environment_config()
    assert "unsafe" in str(exc_info.value).lower()


def test_default_database_credentials_rejected_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "secure_prod_secret_key_88492048")

    mgr = EnvironmentManager()
    with pytest.raises(UnsafeConfigurationError) as exc_info:
        mgr.load_environment_config()
    assert "Default database credentials" in str(exc_info.value)


def test_secrets_sanitizer_masks_canary_secrets():
    raw_str = "DATABASE_URL=postgresql+asyncpg://user:canary_password_999@localhost:5432/db jwt_secret=password123"
    sanitized = SecretsSanitizer.sanitize_string(raw_str)
    assert "canary_password_999" not in sanitized
    assert "password123" not in sanitized
    assert "[REDACTED" in sanitized


def test_secret_provider_require_secret(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "secret_val")
    provider = EnvironmentSecretProvider()
    assert provider.require_secret("TEST_KEY") == "secret_val"

    with pytest.raises(Exception):
        provider.require_secret("NON_EXISTENT_SECRET_KEY_XYZ")
