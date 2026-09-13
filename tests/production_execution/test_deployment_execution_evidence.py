import pytest
from app.deployment.deployment_execution_evidence import DeploymentExecutionEvidenceCollector


def test_deployment_execution_evidence_collector():
    raw_payload = {
        "step": "INFRASTRUCTURE_VALIDATION",
        "secret_canary": "super_secret_password123",
        "status": "HEALTHY",
    }
    rec = DeploymentExecutionEvidenceCollector.collect_evidence(
        evidence_id="ev-100",
        category="PREFLIGHT",
        execution_status="PASSED",
        payload=raw_payload,
    )

    assert rec.evidence_id == "ev-100"
    assert rec.fingerprint.startswith("sha256:")
    assert "password123" not in str(rec.sanitized_payload)
