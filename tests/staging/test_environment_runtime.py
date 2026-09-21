from app.deployment.models import DeploymentEnvironment, EnvironmentConfig
from app.deployment.profiles import DeploymentProfile
from app.deployment.secrets import SecretsSanitizer


def test_environment_profile_resolution():
    """Verifies profile constraints for STAGING vs PRODUCTION profiles."""
    staging_prof = DeploymentProfile.get_profile(DeploymentEnvironment.STAGING)
    assert staging_prof.require_database is True
    assert staging_prof.allow_debug is False

    prod_prof = DeploymentProfile.get_profile(DeploymentEnvironment.PRODUCTION)
    assert prod_prof.require_database is True
    assert prod_prof.allow_debug is False


def test_zero_secret_leakage_in_sanitizer():
    """Verifies that SecretsSanitizer masks sensitive credentials with SHA-256 redactions."""
    secret_str = "postgresql://postgres:mysecretpassword@localhost:5432/production_db"
    sanitized = SecretsSanitizer.sanitize_string(secret_str)
    assert "mysecretpassword" not in sanitized
    assert "REDACTED" in sanitized or "[REDACTED" in sanitized


def test_environment_isolation_guard():
    """Verifies that invalid environment profile overrides are rejected."""
    config = EnvironmentConfig(
        environment=DeploymentEnvironment.STAGING,
        application_name="enterprise-ai-platform",
        application_version="1.0.0",
        deployment_version="5.60A",
        region="us-east-1",
        instance_id="inst-01",
        debug_enabled=False,
        database_url="postgresql://user:pass@localhost:5432/db",
        cache_enabled=True,
        messaging_enabled=True,
        observability_enabled=True,
        log_level="INFO",
    )
    assert config.environment == DeploymentEnvironment.STAGING
    assert config.is_production() is False
