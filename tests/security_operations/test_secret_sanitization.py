"""
Tests for Secret Sanitization across Phase 5.69 outputs (Phase 5.69).
"""

import pytest
from app.deployment.secrets import get_secrets_sanitizer
from app.security_operations.security_operations_orchestrator import SecurityOperationsOrchestrator


def test_secret_sanitization_in_orchestrator_results():
    sanitizer = get_secrets_sanitizer()
    orchestrator = SecurityOperationsOrchestrator()

    # Pass environment with secret canary
    env_config = {
        "SECRET_KEY": "super_secret_test_value",
        "PORT": "8080",
    }

    result = orchestrator.run_security_assessment(
        target_name="Sanitization-Test",
        env_config=env_config,
        is_production=False,
    )

    res_dict = result.to_dict()
    res_str = str(res_dict)

    # Ensure secret canary value is never present unredacted in output dict/str
    assert "super_secret_test_value" not in res_str
    assert "[REDACTED" in res_str
