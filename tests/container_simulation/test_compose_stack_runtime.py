import os

import pytest

from app.deployment.container_validation import DockerPreflightValidator


def test_compose_stack_configuration_integrity():
    assert os.path.exists("docker-compose.production-simulation.yml")
    assert os.path.exists(".env.production.simulation")


def test_compose_stack_runtime_or_preflight_gating():
    preflight = DockerPreflightValidator.check_docker_daemon()
    if not preflight["available"]:
        pytest.skip("Docker daemon not available on host environment")
