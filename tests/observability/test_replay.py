"""Tests for ExecutionReplayManager and safe replay mode."""

import pytest
from app.observability.replay import ExecutionReplayManager
from app.observability.context import ObservabilityContext
from app.observability.exceptions import ExecutionNotFoundException, ReplayNotAvailableException


@pytest.mark.asyncio
async def test_replay_snapshot_and_safe_mode():
    rm = ExecutionReplayManager()
    ctx = ObservabilityContext(tenant_id="ten-r1")

    rm.create_snapshot(
        execution_id="exec-r1",
        component="tool",
        inputs={"param": "test"},
        config={"model": "gpt-4"},
        is_high_risk=True,
        context=ctx,
    )

    # Safe replay mode should reject high-risk external side-effects when not forced
    with pytest.raises(ReplayNotAvailableException):
        await rm.replay_execution("exec-r1", force_external_effects=False, tenant_id="ten-r1")

    # Approved force_external_effects replay should succeed
    res = await rm.replay_execution("exec-r1", force_external_effects=True, tenant_id="ten-r1")
    assert res["status"] == "COMPLETED"
    assert res["comparison"]["matched"] is True


def test_tenant_isolation_in_replay():
    rm = ExecutionReplayManager()
    rm.create_snapshot("exec-isolation", "agent", {}, {}, context=ObservabilityContext(tenant_id="tenant-A"))

    with pytest.raises(ExecutionNotFoundException):
        rm.get_snapshot("exec-isolation", tenant_id="tenant-B")
