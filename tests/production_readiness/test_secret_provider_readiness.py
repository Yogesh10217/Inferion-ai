from __future__ import annotations

from app.deployment.secrets import SecretProviderReadinessEvaluator, SecretsSanitizer


def test_secret_provider_readiness_canary_rejection(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "change_me")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://sim_user:sim_pass@localhost:5432/test_db")

    res = SecretProviderReadinessEvaluator.evaluate_secret_provider_readiness(is_production=True)

    assert res["status"] == "BLOCKED"
    assert res["default_secrets_rejected"] is False
    assert "JWT_SECRET" in res["canary_secrets"]
    assert res["classification"] == "SECRET_PROVIDER_RUNTIME_NOT_EXECUTED"


def test_secret_sanitizer_masks_credentials():
    raw_str = "postgresql://sim_user:secret_pass_123@localhost:5432/db?token=secret123"
    sanitized = SecretsSanitizer.sanitize_string(raw_str)

    assert "secret_pass_123" not in sanitized
    assert "secret123" not in sanitized
    assert "[REDACTED" in sanitized
