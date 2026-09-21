"""
Tests for API Security Evaluator (Phase 5.69).
"""

from app.security_operations.api_security import APISecurityEvaluator, APISecurityResult


def test_api_security_evaluation():
    evaluator = APISecurityEvaluator()
    config = {
        "hsts_enabled": True,
        "csp_enabled": True,
        "x_frame_options": "DENY",
        "cors_origins": ["https://app.enterprise.ai"],
        "rate_limiting_enabled": True,
        "docs_disabled_in_prod": True,
    }
    result = evaluator.evaluate(api_config=config, is_production=True)
    assert isinstance(result, APISecurityResult)
    assert result.hsts_enabled is True
    assert result.docs_protected_in_prod is True
    assert result.score == 100.0
