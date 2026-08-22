"""Unit tests for IdentityLifecycleManager access review workflows."""

import pytest
from app.identity.lifecycle import IdentityLifecycleManager, ReviewStatus


def test_access_review_workflow():
    mgr = IdentityLifecycleManager()

    rev = mgr.initiate_access_review("user_dev", role="admin", tenant_id="t_life")
    assert rev.status == ReviewStatus.PENDING

    cert_rev = mgr.certify_access(rev.review_id, reviewer_id="sec_admin")
    assert cert_rev.status == ReviewStatus.APPROVED
    assert cert_rev.reviewer_id == "sec_admin"
