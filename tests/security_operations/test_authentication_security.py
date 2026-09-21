"""
Tests for Authentication Security Evaluator (Phase 5.69).
"""

from app.security_operations.authentication_security import (
    AuthenticationSecurityEvaluator,
    AuthenticationSecurityResult,
)


def test_authentication_security_evaluation():
    evaluator = AuthenticationSecurityEvaluator()
    config = {
        "auth_enabled": True,
        "mfa_enabled": True,
        "session_timeout_seconds": 900,
        "jwt_algo": "RS256",
        "lockout_policy_enabled": True,
    }
    result = evaluator.evaluate(auth_config=config, is_production=True)
    assert isinstance(result, AuthenticationSecurityResult)
    assert result.mfa_enforced is True
    assert result.score == 100.0
