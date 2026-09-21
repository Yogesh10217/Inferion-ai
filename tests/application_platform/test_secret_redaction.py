"""Unit tests for Secret Redaction & Sanitization."""

from app.application_platform.interactions import InteractionManager


def test_interaction_secret_redaction():
    mgr = InteractionManager()
    sanitized = mgr.sanitize_text("Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456")
    assert "abcdef" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized
