"""Unit tests for AccessControlManager evaluation."""

import pytest
from app.identity.access_control import AccessControlManager, AccessContext, AccessDecisionType


def test_access_control_evaluation():
    mgr = AccessControlManager()

    # Standard access -> ALLOW
    ctx_std = AccessContext(identity_id="user_1", role="developer", data_classification="INTERNAL")
    res_std = mgr.evaluate_access("read", ctx_std)
    assert res_std.decision == AccessDecisionType.ALLOW

    # Restricted data without HIGH assurance -> REQUIRE_STEP_UP_AUTH
    ctx_restr = AccessContext(identity_id="user_1", role="analyst", data_classification="RESTRICTED", authentication_level="STANDARD")
    res_restr = mgr.evaluate_access("read", ctx_restr)
    assert res_restr.decision == AccessDecisionType.REQUIRE_STEP_UP_AUTH
    assert res_restr.required_assurance == "HIGH"
