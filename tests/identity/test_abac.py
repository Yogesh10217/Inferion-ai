"""Unit tests for ABAC risk score and attribute evaluation."""

from app.identity.access_control import AccessContext, AccessControlManager, AccessDecisionType


def test_abac_elevated_risk_approval():
    mgr = AccessControlManager()

    ctx_risk = AccessContext(identity_id="user_2", risk_score=85.0)
    res_risk = mgr.evaluate_access("write", ctx_risk)

    assert res_risk.decision == AccessDecisionType.REQUIRE_APPROVAL
    assert res_risk.approval_request_id is not None
