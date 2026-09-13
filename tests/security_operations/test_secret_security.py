"""
Tests for Secret Security Evaluator (Phase 5.69).
"""

import pytest
from app.security_operations.secret_security import SecretSecurityEvaluator, SecretSecurityResult


def test_secret_security_clean_env():
    evaluator = SecretSecurityEvaluator()
    env = {
        "PORT": "8000",
        "ENV": "production",
    }
    result = evaluator.evaluate(env_config=env)
    assert isinstance(result, SecretSecurityResult)
    assert result.hardcoded_secrets_detected == 0
    assert result.canary_leaks_detected == 0
    assert result.score == 100.0


def test_secret_security_canary_leak():
    evaluator = SecretSecurityEvaluator()
    env = {
        "DEBUG_KEY": "super_secret_test_value",
    }
    result = evaluator.evaluate(env_config=env)
    assert result.canary_leaks_detected >= 1
    assert result.score < 100.0
