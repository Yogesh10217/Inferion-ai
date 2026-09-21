from app.deployment.deployment_authorization import DeploymentAuthorizationEngine
from app.deployment.models import DeploymentAuthorizationStatus


def test_authorization_request_creation():
    rec = DeploymentAuthorizationEngine.create_authorization_request(
        release_candidate_id="rc-100",
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        git_revision="git-rev-100",
    )
    assert rec.status == DeploymentAuthorizationStatus.PENDING
    assert len(rec.approved_categories) == 0
    assert rec.fingerprint.startswith("sha256:")


def test_full_authorization_approval_path():
    rec = DeploymentAuthorizationEngine.create_authorization_request(
        release_candidate_id="rc-100",
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        git_revision="git-rev-100",
    )
    categories = ["TECHNICAL", "SECURITY", "DATABASE", "OPERATIONS", "RELEASE", "DEPLOYMENT_EXECUTOR"]
    for cat in categories:
        rec = DeploymentAuthorizationEngine.grant_category_approval(
            record=rec,
            category=cat,
            approver=f"approver-{cat.lower()}",
            current_artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
            current_git_revision="git-rev-100",
        )

    assert rec.status == DeploymentAuthorizationStatus.AUTHORIZED
    val = DeploymentAuthorizationEngine.validate_authorization_for_execution(
        record=rec,
        target_artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        target_git_revision="git-rev-100",
    )
    assert val["valid"] is True
    assert len(val["missing_categories"]) == 0
