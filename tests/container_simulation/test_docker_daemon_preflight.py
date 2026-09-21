from app.deployment.container_validation import DockerPreflightValidator


def test_docker_daemon_preflight_returns_structured_result():
    res = DockerPreflightValidator.check_docker_daemon()
    assert "available" in res
    assert "status" in res
    assert res["status"] in ("DOCKER_DAEMON_AVAILABLE", "DOCKER_DAEMON_NOT_AVAILABLE")
    assert isinstance(res["available"], bool)
