import pytest
from app.deployment.container_validation import DockerPreflightValidator, ContainerValidationEngine


def test_container_image_build_orchestration_or_preflight_gating():
    preflight = DockerPreflightValidator.check_docker_daemon()
    if not preflight["available"]:
        pytest.skip("Docker daemon not available on host environment")

    # If Docker is available, validate container environment manifest
    info = ContainerValidationEngine.validate_container_environment("enterprise-ai-platform:production-simulation", is_production=True)
    assert info["image_tag_valid"] is True
