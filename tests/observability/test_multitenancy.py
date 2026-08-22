"""Tests for multi-tenant isolation in Observability subsystem."""

import pytest
from app.observability.manager import ObservabilityManager
from app.observability.context import ObservabilityContext
from app.observability.exceptions import ExecutionNotFoundException


def test_multitenant_cost_isolation():
    manager = ObservabilityManager()

    ctx_a = ObservabilityContext(tenant_id="tenant-A", workspace_id="ws-A")
    ctx_b = ObservabilityContext(tenant_id="tenant-B", workspace_id="ws-B")

    manager.cost_tracker.record_usage(input_tokens=1000, output_tokens=500, model="gpt-4o", context=ctx_a)
    manager.cost_tracker.record_usage(input_tokens=2000, output_tokens=1000, model="gpt-4o", context=ctx_b)

    cost_a = manager.cost_tracker.get_tenant_cost("tenant-A")
    cost_b = manager.cost_tracker.get_tenant_cost("tenant-B")

    assert cost_a["total_tokens"] == 1500
    assert cost_b["total_tokens"] == 3000


def test_replay_tenant_isolation():
    manager = ObservabilityManager()
    manager.replay_manager.create_snapshot(
        execution_id="exec-tenant-x",
        component="agent",
        inputs={},
        config={},
        context=ObservabilityContext(tenant_id="tenant-X"),
    )

    with pytest.raises(ExecutionNotFoundException):
        manager.replay_manager.get_snapshot("exec-tenant-x", tenant_id="tenant-Y")
