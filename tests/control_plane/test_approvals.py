"""Unit tests for High-Risk Approval Integration."""

import pytest

from app.control_plane.admin_operations import AdminOperationsManager
from app.control_plane.exceptions import ApprovalRequiredException


def test_high_risk_approval_gating():
    ops = AdminOperationsManager()

    # Attempting high-risk action without approval flag raises ApprovalRequiredException
    with pytest.raises(ApprovalRequiredException) as exc_info:
        ops.execute_operation(action="emergency_stop_activate", target_id="global")

    assert exc_info.value.code == "APPROVAL_REQUIRED"

    # Approving request allows execution
    res = ops.execute_operation(action="emergency_stop_activate", target_id="global", approved=True)
    assert res.status == "COMPLETED"
