import pytest
from app.deployment.deployment_authorization import DeploymentAuthorizationEngine
from app.deployment.models import DeploymentAuthorizationStatus


def test_artifact_digest_mismatch_invalidates_authorization():
    rec = DeploymentAuthorizationEngine.create_authorization_request(
        release_candidate_id="rc-100",
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        git_revision="git-rev-100",
    )

    # Attempt signoff with altered digest
    rec = DeploymentAuthorizationEngine.grant_category_approval(
        record=rec,
        category="TECHNICAL",
        approver="tech-lead",
        current_artifact_digest="sha256:ALTERED_DIGEST_HASH_999999999999999999999999999999999999",
        current_git_revision="git-rev-100",
    )

    assert rec.status == DeploymentAuthorizationStatus.REJECTED
    assert "DEPLOYMENT_ARTIFACT_MISMATCH" in rec.metadata.get("rejection_reason", "")
