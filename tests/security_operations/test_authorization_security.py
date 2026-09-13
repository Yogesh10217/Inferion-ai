"""
Tests for Authorization Security Evaluator (Phase 5.69).
"""

import pytest
from app.security_operations.authorization_security import AuthorizationSecurityEvaluator, AuthorizationSecurityResult


def test_authorization_security_evaluation():
    evaluator = AuthorizationSecurityEvaluator()
    config = {
        "rbac_enabled": True,
        "abac_enabled": True,
        "least_privilege_enforced": True,
        "wildcard_permissions_allowed": False,
        "default_deny": True,
    }
    result = evaluator.evaluate(authz_config=config, is_production=True)
    assert isinstance(result, AuthorizationSecurityResult)
    assert result.rbac_enabled is True
    assert result.least_privilege_enforced is True
    assert result.score == 100.0
