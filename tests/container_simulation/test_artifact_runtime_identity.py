import pytest
from app.deployment.container_validation import DockerPreflightValidator, ContainerValidationEngine


def test_artifact_runtime_identity_matching_logic():
    exp = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    act = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    match, msg = ContainerValidationEngine.validate_runtime_artifact(exp, act)
    assert match is True

    mismatch_act = "sha256:1111111111111111111111111111111111111111111111111111111111111111"
    match, msg = ContainerValidationEngine.validate_runtime_artifact(exp, mismatch_act)
    assert match is False
    assert "DEPLOYMENT_ARTIFACT_MISMATCH" in msg


def test_artifact_runtime_identity_or_preflight_gating():
    preflight = DockerPreflightValidator.check_docker_daemon()
    if not preflight["available"]:
        pytest.skip("Docker daemon not available on host environment")
