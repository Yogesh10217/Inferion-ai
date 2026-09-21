"""Unit tests for Application Configuration & Environment Management."""

from app.application_platform.configuration import (
    ApplicationEnvironment,
    ConfigurationManager,
)
from app.security.secrets import SecretManager


def test_configuration_environment_isolation_and_secrets():
    sec_mgr = SecretManager()
    sec_mgr.set_secret("API_KEY_SEC", "super_secret_value_123")

    cfg_mgr = ConfigurationManager(secret_manager=sec_mgr)

    cfg = cfg_mgr.set_environment_config(
        tenant_id="t1",
        application_id="app_1",
        environment=ApplicationEnvironment.STAGING,
        secret_references={"api_key": "API_KEY_SEC"},
    )

    resolved = cfg_mgr.resolve_secret(cfg.secret_references["api_key"])
    assert resolved == "super_secret_value_123"
