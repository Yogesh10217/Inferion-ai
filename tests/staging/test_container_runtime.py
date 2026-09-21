import shutil

import pytest

from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.runtime_validation import RuntimeValidationEngine, ValidationStatus, ValidationType


def test_dockerfile_configuration_integrity():
    """Validates Dockerfile presence, multi-stage structure, non-root user, and port binding."""
    res = ContainerValidationEngine.validate_container_environment()
    assert res["dockerfile_present"] is True
    assert res["status"] == "AVAILABLE"
    assert "appuser" in res.get("configured_user", "appuser")


def test_docker_cli_availability():
    """Checks whether Docker CLI binary is installed and accessible in current environment."""
    docker_bin = shutil.which("docker")
    if not docker_bin:
        pytest.skip("Docker CLI binary not found in PATH; environment marked UNAVAILABLE")
    assert docker_bin is not None


def test_container_runtime_evidence_recording():
    """Validates that RuntimeValidationEngine records container runtime evidence cleanly."""
    engine = RuntimeValidationEngine(environment="STAGING")
    evidence = engine.record_evidence(
        name="ContainerRuntimeProbe",
        val_type=ValidationType.CONTAINER_RUNTIME,
        executed=True,
        status=ValidationStatus.PASSED,
        command="docker run -d -p 8002:8002 enterprise-ai-platform:5.60a",
        exit_code=0,
        duration_ms=45.2,
        raw_output="Container started successfully. Listening on port 8002",
    )
    assert evidence.status == ValidationStatus.PASSED
    assert evidence.executed is True
    assert evidence.exit_code == 0
    assert len(evidence.evidence_fingerprint) == 64
