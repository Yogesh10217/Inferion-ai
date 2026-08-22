"""Unit tests for refresh token rotation."""

import pytest
from app.identity.session import SessionManager


def test_refresh_token_rotation():
    mgr = SessionManager()
    sess = mgr.create_session("user_rot", tenant_id="t_tok")

    old_access = sess.access_token
    old_refresh = sess.refresh_token

    rot_sess = mgr.rotate_tokens(sess.session_id, old_refresh)

    assert rot_sess.access_token != old_access
    assert rot_sess.refresh_token != old_refresh
