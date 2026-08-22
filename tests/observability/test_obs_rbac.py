"""Tests for RBAC permission enforcement in Observability Replay."""

import pytest
from app.observability.replay import ExecutionReplayManager
from app.observability.context import ObservabilityContext
from app.observability.exceptions import ReplayNotAvailableException


@pytest.mark.asyncio
async def test_replay_rbac_permission_check():
    rm = ExecutionReplayManager()
    rm.create_snapshot(
        execution_id="exec-rbac-1",
        component="agent",
        inputs={},
        config={},
        is_high_risk=False,
        context=ObservabilityContext(tenant_id="tenant-rbac"),
    )

    # User lacking permission should be rejected
    with pytest.raises(ReplayNotAvailableException):
        await rm.replay_execution(
            execution_id="exec-rbac-1",
            tenant_id="tenant-rbac",
            user_permissions=["read:metrics"],  # Missing 'replay:execute'
        )

    # User with permission should succeed
    res = await rm.replay_execution(
        execution_id="exec-rbac-1",
        tenant_id="tenant-rbac",
        user_permissions=["replay:execute"],
    )
    assert res["status"] == "COMPLETED"
