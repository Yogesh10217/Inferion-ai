"""
Tests for Container Security Evaluator (Phase 5.69).
"""

from app.security_operations.container_security import ContainerSecurityEvaluator, ContainerSecurityResult


def test_container_security_evaluation():
    evaluator = ContainerSecurityEvaluator()
    config = {
        "user": "appuser",
        "read_only_root_fs": True,
        "allow_privilege_escalation": False,
        "exposed_ports": [8080],
        "image_digest": "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    }
    result = evaluator.evaluate(container_config=config, is_production=True)
    assert isinstance(result, ContainerSecurityResult)
    assert result.is_non_root is True
    assert result.is_read_only_root_fs is True
    assert result.score == 100.0
