"""Unit tests for SessionManager state, restrictions, and forced revocation."""

import pytest
from app.identity.session import SessionManager, SessionState
from app.identity.exceptions import SessionRevokedException


def test_session_lifecycle_and_forced_revocation():
    mgr = SessionManager()

    sess = mgr.create_session("user_sess", tenant_id="t_sess")
    assert sess.state == SessionState.ACTIVE

    # Restrict session
    r_sess = mgr.restrict_session(sess.session_id, reason="Suspicious IP")
    assert r_sess.state == SessionState.RESTRICTED
    assert r_sess.is_restricted is True

    # Revoke session
    rev_sess = mgr.revoke_session(sess.session_id, reason="Security threat")
    assert rev_sess.state == SessionState.REVOKED

    # Attempt access on revoked session -> Exception
    with pytest.raises(SessionRevokedException):
        mgr.get_session(sess.session_id)
