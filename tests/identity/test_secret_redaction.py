"""Unit tests for automated SecretManager secret redaction in session & credential metadata."""

import pytest
from app.security.secrets import SecretManager


def test_secret_redaction_in_identity_strings():
    mgr = SecretManager()
    token_str = "Bearer sk-proj-1234567890abcdef1234567890"

    sanitized = mgr.sanitize_text(token_str)
    assert "sk-proj-1234567890abcdef1234567890" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized or "sk-" not in sanitized
