"""Unit tests for RBAC role-based access checks."""

import pytest
from app.identity.access_control import AccessControlManager, AccessContext, AccessDecisionType


def test_rbac_guest_denial():
    mgr = AccessControlManager()

    ctx_guest = AccessContext(identity_id="guest_user", role="guest")
    res_guest = mgr.evaluate_access("admin_override", ctx_guest)

    assert res_guest.decision == AccessDecisionType.DENY
    assert res_guest.allow is False
