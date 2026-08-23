"""Unit tests for Human Decision Collaboration & Approval Integration."""

import pytest
from app.intelligence_platform.recommendations import RecommendationManager, RecommendationType
from app.intelligence_platform.human_decisions import DecisionApprovalManager, ReviewAction, DecisionReviewer


def test_human_approval_request_and_decision():
    rec_mgr = RecommendationManager()
    rec = rec_mgr.create_recommendation("t1", RecommendationType.ROLLBACK_DEPLOYMENT, "High Risk Action", "Rollback DB", "db_prod", "Impact", risk_level="HIGH")

    approval_mgr = DecisionApprovalManager()
    rev = approval_mgr.request_human_approval("t1", rec)

    assert rev.status == "PENDING"
    assert rev.approval_request_id is not None

    reviewer = DecisionReviewer(user_id="admin_1")
    updated = approval_mgr.submit_review_decision("t1", rev.review_id, reviewer, ReviewAction.APPROVE, comments="Approved for production safety")

    assert updated.status == "APPROVED"
