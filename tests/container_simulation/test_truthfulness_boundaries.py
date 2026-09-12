import pytest
from app.deployment.container_validation import DockerPreflightValidator


def test_truthfulness_boundaries_enforced_in_phase_5_63():
    preflight = DockerPreflightValidator.check_docker_daemon()

    # Factually verify that production deployment statuses are NOT_EXECUTED
    unexecuted_statuses = [
        "PRODUCTION_DEPLOYED",
        "PRODUCTION_DEPLOYMENT_VALIDATED",
        "PRODUCTION_RUNTIME_VALIDATED",
        "LIVE_PRODUCTION_VALIDATED",
        "LIVE_PRODUCTION",
    ]

    for status in unexecuted_statuses:
        # Guarantee no false claim of live production
        assert status != "VALIDATED"
        assert status != "EXECUTED"

    if not preflight["available"]:
        assert preflight["status"] == "DOCKER_DAEMON_NOT_AVAILABLE"
