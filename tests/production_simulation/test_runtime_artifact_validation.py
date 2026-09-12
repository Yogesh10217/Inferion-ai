import pytest
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.deployment_metadata import DeploymentIdentityBuilder
from app.deployment.exceptions import ConfigurationValidationError
from app.deployment.models import EnvironmentConfig, DeploymentEnvironment


def test_valid_sha256_digest_validation():
    valid_digest = "sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
    valid, msg = ContainerValidationEngine.validate_image_digest(valid_digest)
    assert valid is True
    assert "valid sha256" in msg.lower()

    valid_at, msg_at = ContainerValidationEngine.validate_image_digest("@" + valid_digest)
    assert valid_at is True


def test_invalid_and_malformed_digest_validation():
    invalid_digests = [
        "",
        "NOT_AVAILABLE",
        "md5:11112222333344445555666677778888",
        "sha256:short_hash",
        "sha256:invalid_chars_xyz_1111222233334444555566667777888899990000aaaa",
    ]
    for dig in invalid_digests:
        valid, msg = ContainerValidationEngine.validate_image_digest(dig)
        assert valid is False


test_valid_digest = "sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
test_mismatch_digest = "sha256:9999999999999999999999999999999999999999aaaabbbbccccddddeeeeffff"


def test_runtime_artifact_digest_match():
    match, msg = ContainerValidationEngine.validate_runtime_artifact(test_valid_digest, test_valid_digest)
    assert match is True
    assert "matches expected" in msg.lower()


def test_runtime_artifact_digest_mismatch():
    match, msg = ContainerValidationEngine.validate_runtime_artifact(test_valid_digest, test_mismatch_digest)
    assert match is False
    assert "DEPLOYMENT_ARTIFACT_MISMATCH" in msg


def test_deployment_identity_builder_require_digest():
    config = EnvironmentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        application_name="Platform",
        application_version="1.0.0",
        deployment_version="5.62",
        region="us-east-1",
        instance_id="node-1",
        debug_enabled=False,
        database_url="postgresql://db:5432/db",
        cache_enabled=True,
        messaging_enabled=True,
        observability_enabled=True,
        log_level="INFO",
    )

    # Missing digest when required must fail
    import os
    os.environ["IMAGE_DIGEST"] = "NOT_AVAILABLE"
    with pytest.raises(ConfigurationValidationError):
        DeploymentIdentityBuilder.build_identity(config, require_digest=True)

    # Valid digest must succeed
    os.environ["IMAGE_DIGEST"] = test_valid_digest
    identity = DeploymentIdentityBuilder.build_identity(config, require_digest=True)
    assert identity.image_digest == test_valid_digest
