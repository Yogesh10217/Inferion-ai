"""Unit tests for Interactions & Secret Sanitization."""

from app.application_platform.interactions import InteractionManager


def test_interaction_secret_sanitization():
    mgr = InteractionManager()

    raw_input = "My API key is sk-123456789012345678901234567890"
    turn = mgr.add_interaction(
        tenant_id="t1",
        conversation_id="conv_1",
        user_input=raw_input,
        system_response="Received response for password='mysecretpassword'",
    )

    assert "sk-12345" not in turn.sanitized_input
    assert "[REDACTED_SECRET]" in turn.sanitized_input
    assert "[REDACTED_SECRET]" in turn.sanitized_response
