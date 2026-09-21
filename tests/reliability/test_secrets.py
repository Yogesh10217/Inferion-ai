"""Unit tests for SecretManager and auto-redaction."""

from app.security.secrets import SecretManager


def test_secret_redaction():
    secret_mgr = SecretManager()
    secret_mgr.register_secret_value("super_secret_token_12345")

    text = "Logging payload with api_key=super_secret_token_12345 and sensitive info"
    sanitized = secret_mgr.sanitize_text(text)

    assert "super_secret_token_12345" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized
