"""Unit tests for secret redaction in knowledge content."""

import pytest
from app.security.secrets import SecretManager


def test_secret_redaction_in_knowledge_content():
    mgr = SecretManager()
    content = "Config API KEY=sk-proj-9876543210fedcba9876543210"

    sanitized = mgr.sanitize_text(content)
    assert "sk-proj-9876543210fedcba9876543210" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized or "sk-" not in sanitized
