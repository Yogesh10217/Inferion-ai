"""Unit tests for AdminOperationsManager."""

import pytest

from app.control_plane.admin_operations import AdminOperationsManager
from app.control_plane.exceptions import ApprovalRequiredException


def test_admin_operation_and_emergency_stop():
    ops = AdminOperationsManager()

    # Normal operation
    res = ops.execute_operation(action="restart_workers", target_id="pool_1")
    assert res.status == "COMPLETED"

    # Emergency stop activate requires approval
    with pytest.raises(ApprovalRequiredException):
        ops.execute_operation(action="activate_emergency_stop", target_id="global")

    # Approved emergency stop
    res_appr = ops.execute_operation(action="activate_emergency_stop", target_id="global", approved=True)
    assert res_appr.status == "COMPLETED"
    assert ops.emergency_stop_active is True
