"""Unit tests for access review retrieval."""

from app.identity.lifecycle import IdentityLifecycleManager


def test_access_review_retrieval():
    mgr = IdentityLifecycleManager()
    rev = mgr.initiate_access_review("user_ops", role="operator", tenant_id="t_ar")

    fetched = mgr.get_review(rev.review_id)
    assert fetched.identity_id == "user_ops"
    assert fetched.role == "operator"
