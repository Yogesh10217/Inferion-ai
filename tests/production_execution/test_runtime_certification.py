import pytest
from app.deployment.models import RuntimeCertificationStatus
from app.deployment.production_runtime_certification import ProductionRuntimeCertificationEngine


def test_simulation_runtime_certification():
    cert = ProductionRuntimeCertificationEngine.certify_runtime(
        deployment_id="dep-sim-01",
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        environment="STAGING",
        adapter_type="SIMULATION",
        execution_evidence={"test": "passed"},
        health_validated=True,
        smoke_tests_passed=True,
        traffic_validated=True,
    )
    assert cert.runtime_status == RuntimeCertificationStatus.VALIDATED
    assert cert.evidence_level == "SIMULATION_RUNTIME"
    assert cert.truthfulness_status == "SIMULATION_RUNTIME_VALIDATED"
    assert cert.evidence_fingerprint.startswith("sha256:")


def test_container_runtime_certification():
    cert = ProductionRuntimeCertificationEngine.certify_runtime(
        deployment_id="dep-cont-01",
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        environment="STAGING",
        adapter_type="CONTAINER",
        execution_evidence={"test": "passed"},
        health_validated=True,
        smoke_tests_passed=True,
        traffic_validated=True,
    )
    assert cert.runtime_status == RuntimeCertificationStatus.VALIDATED
    assert cert.evidence_level == "CONTAINER_RUNTIME"
    assert cert.truthfulness_status == "CONTAINER_RUNTIME_VALIDATED"
