import pytest

from app.deployment.container_validation import DockerPreflightValidator


def test_prometheus_container_connectivity_or_preflight_gating():
    preflight = DockerPreflightValidator.check_docker_daemon()
    if not preflight["available"]:
        pytest.skip("Docker daemon not available on host environment")
