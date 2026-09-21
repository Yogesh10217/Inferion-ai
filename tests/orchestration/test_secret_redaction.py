"""Unit tests for secret redaction in task inputs and execution metadata."""

from app.security.secrets import SecretManager


def test_secret_redaction_in_orchestration_metadata():
    mgr = SecretManager()
    payload = "API_KEY=sk-proj-9876543210fedcba9876543210"

    sanitized = mgr.sanitize_text(payload)
    assert "sk-proj-9876543210fedcba9876543210" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized or "sk-" not in sanitized
