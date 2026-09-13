import pytest
from app.deployment.deployment_failure_detector import DeploymentFailureDetector
from app.deployment.models import ProductionDeploymentState, RollbackTrigger


def test_failure_detector_mapping():
    rec_art = DeploymentFailureDetector.detect_failure("DEPLOYMENT_ARTIFACT_MISMATCH", "Digest changed mid-pipeline")
    assert rec_art.rollback_trigger == RollbackTrigger.DEPLOYMENT_ARTIFACT_MISMATCH
    assert rec_art.rollback_required is True

    rec_sec = DeploymentFailureDetector.detect_failure("SECURITY_POLICY_VIOLATION", "Canary secret leak detected")
    assert rec_sec.rollback_trigger == RollbackTrigger.SECURITY_POLICY_VIOLATION
    assert rec_sec.rollback_required is True
