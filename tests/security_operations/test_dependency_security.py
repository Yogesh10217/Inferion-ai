"""
Tests for Dependency Security Evaluator (Phase 5.69).
"""

from app.security_operations.dependency_security import DependencySecurityEvaluator, DependencySecurityResult


def test_dependency_security_evaluation():
    evaluator = DependencySecurityEvaluator()
    manifest = {
        "requests": "2.31.0",
        "urllib3": "1.26.5",
    }
    result = evaluator.evaluate(package_manifest=manifest)
    assert isinstance(result, DependencySecurityResult)
    assert 0.0 <= result.score <= 100.0
    assert result.total_dependencies == 2
    assert result.fingerprint.startswith("sha256:")
