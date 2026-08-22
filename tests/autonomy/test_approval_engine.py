"""
Tests for Human Approval Engine
"""

import pytest
from app.approvals.approval_engine import ApprovalEngine
from app.approvals.approval_request import ApprovalStatus
from app.approvals.approval_policies import RiskLevel


def test_approval_request_workflow():
    engine = ApprovalEngine()
    req = engine.request_approval(
        execution_id="exec_high_risk",
        action_type="database_write",
        risk_level=RiskLevel.HIGH,
    )
    assert req.status == ApprovalStatus.PENDING

    appr = engine.approve(req.request_id, approver_id="security_lead")
    assert appr.status == ApprovalStatus.APPROVED
    assert appr.approver == "security_lead"
