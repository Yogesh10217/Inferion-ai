"""Unit tests for Personalization & Consent Boundaries."""

from app.application_platform.personalization import (
    ConsentScope,
    ConsentStatus,
    PersonalizationEngine,
)


def test_personalization_respects_explicit_consent():
    engine = PersonalizationEngine()
    engine.set_profile("t1", "user_alice", {"theme": "DARK", "language": "en"})

    # Prior to consent, profile preferences are not returned
    ctx_before = engine.construct_experience_context("t1", "user_alice", "app_1")
    assert ctx_before.allowed_preferences == {}

    # Grant USER_PROFILE consent
    engine.grant_consent("t1", "user_alice", ConsentScope.USER_PROFILE, ConsentStatus.GRANTED)
    ctx_after = engine.construct_experience_context("t1", "user_alice", "app_1")
    assert ctx_after.allowed_preferences["theme"] == "DARK"


def test_memory_access_blocked_without_consent():
    engine = PersonalizationEngine()
    ctx = engine.construct_experience_context("t1", "user_bob", "app_1")
    assert "user:user_bob:private" not in ctx.authorized_memory_scopes

    engine.grant_consent("t1", "user_bob", ConsentScope.MEMORY, ConsentStatus.GRANTED)
    ctx_granted = engine.construct_experience_context("t1", "user_bob", "app_1")
    assert "user:user_bob:private" in ctx_granted.authorized_memory_scopes
