import pytest
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.deployment_metadata import DeploymentIdentityBuilder
from app.deployment.exceptions import ConfigurationValidationError
from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


@pytest.mark.parametrize("bad_tag", ["latest", "dev", "development", "test", "local"])
def test_ambiguous_image_tags_rejected_in_production(bad_tag, monkeypatch):

    valid, msg = ContainerValidationEngine.validate_image_tag(bad_tag, is_production=True)
    assert not valid
    assert "rejected" in msg or "empty" in msg

    monkeypatch.setenv("IMAGE_TAG", bad_tag)
    cfg = EnvironmentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        application_name="Enterprise-AI",
        application_version="1.2.0",
        deployment_version="5.61.0",
        region="us-east-1",
        instance_id="prod-inst-01",
        debug_enabled=False,
        database_url="postgresql+asyncpg://user:pass@prod-db:5432/app",
        cache_enabled=True,
        messaging_enabled=False,
        observability_enabled=True,
        log_level="INFO",
    )
    with pytest.raises(ConfigurationValidationError):
        DeploymentIdentityBuilder.build_identity(cfg)


def test_explicit_versioned_image_tag_accepted():
    valid, msg = ContainerValidationEngine.validate_image_tag("enterprise-ai-platform:5.61.0", is_production=True)
    assert valid
    assert "production-safe" in msg
