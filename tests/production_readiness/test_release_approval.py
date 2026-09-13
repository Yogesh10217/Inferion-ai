from __future__ import annotations

import pytest
from app.deployment.release_approval import ApprovalCategory, ApprovalRequirement, ApprovalStatus, ReleaseApprovalEngine


def test_default_approvals_require_manual_review():
    res = ReleaseApprovalEngine.evaluate_approvals()

    assert res.status == "MANUAL_REVIEW_REQUIRED"
    assert "APPROVAL_RUNTIME_NOT_EXECUTED" in res.classifications


def test_all_approved_grants_approval():
    reqs = [
        ApprovalRequirement(category=ApprovalCategory.TECHNICAL, approver_role="Lead Architect", status=ApprovalStatus.APPROVED),
        ApprovalRequirement(category=ApprovalCategory.SECURITY, approver_role="Security Officer", status=ApprovalStatus.APPROVED),
        ApprovalRequirement(category=ApprovalCategory.DATABASE, approver_role="DBA", status=ApprovalStatus.APPROVED),
        ApprovalRequirement(category=ApprovalCategory.OPERATIONS, approver_role="SRE", status=ApprovalStatus.APPROVED),
        ApprovalRequirement(category=ApprovalCategory.RELEASE, approver_role="Release Manager", status=ApprovalStatus.APPROVED),
    ]

    res = ReleaseApprovalEngine.evaluate_approvals(approvals=reqs)
    assert res.status == "APPROVED"
