from app.deployment.deployment_authorization import DeploymentAuthorizationEngine


def test_authorization_ttl_expiry():
    rec = DeploymentAuthorizationEngine.create_authorization_request(
        release_candidate_id="rc-100",
        artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        git_revision="git-rev-100",
        ttl_seconds=-10,  # Already expired
    )
    assert rec.is_expired() is True

    val = DeploymentAuthorizationEngine.validate_authorization_for_execution(
        record=rec,
        target_artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        target_git_revision="git-rev-100",
    )
    assert val["valid"] is False
    assert any("EXPIRED" in err for err in val["blocking_reasons"])
