import pytest

from app.deployment.deployment_metadata import DeploymentIdentityBuilder, DeploymentMetadataProvider
from app.deployment.exceptions import ConfigurationValidationError
from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


def test_valid_deployment_identity_construction(monkeypatch):
    monkeypatch.delenv("IMAGE_DIGEST", raising=False)
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

    identity = DeploymentIdentityBuilder.build_identity(cfg)
    assert identity.application_version == "1.2.0"
    assert identity.deployment_version == "5.61.0"
    assert identity.environment == "PRODUCTION"
    assert identity.image_tag == "enterprise-ai-platform:5.61.0"
    assert identity.image_digest == "NOT_AVAILABLE"

    metadata = DeploymentMetadataProvider.get_metadata(cfg)
    assert metadata["application_name"] == "Enterprise-AI"
    assert metadata["readiness_classification"] == "PRODUCTION_CONFIGURATION_READY"


def test_empty_deployment_version_rejected():
    cfg = EnvironmentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        application_name="Enterprise-AI",
        application_version="1.2.0",
        deployment_version="",
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
