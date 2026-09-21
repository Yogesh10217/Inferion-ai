"""Unit tests for ZeroTrustEngine continuous evaluation."""

from app.identity.zero_trust import TrustLevel, ZeroTrustAction, ZeroTrustEngine


def test_zero_trust_evaluation_levels():
    engine = ZeroTrustEngine()

    # Trusted evaluation
    res_t = engine.evaluate("user_1", network_trusted=True, device_trusted=True, risk_score=0.0)
    assert res_t.trust_level == TrustLevel.TRUSTED
    assert res_t.recommended_action == ZeroTrustAction.ALLOW

    # Untrusted evaluation (High risk + untrusted network & device)
    res_ut = engine.evaluate("user_1", network_trusted=False, device_trusted=False, risk_score=70.0)
    assert res_ut.trust_level == TrustLevel.UNTRUSTED
    assert res_ut.recommended_action == ZeroTrustAction.TERMINATE_SESSION
