"""
Tests for ToolBillingTracker Accounting
"""

from app.tools.tool_billing import ToolBillingTracker
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult


def test_billing_tracker_usage_accounting():
    tracker = ToolBillingTracker()
    ctx = ToolContext(tenant_id="tenant_bill_1")

    res1 = ToolResult(
        execution_id="e1",
        tool_name="http_tool",
        status=ToolExecutionStatus.SUCCESS,
        execution_time_seconds=1.5,
        cost=0.01,
        compute_usage={"cpu_ms": 1500.0, "memory_mb": 16.0},
        storage_usage={"bytes_read": 1024, "bytes_written": 2048},
        metadata={"external_api_call": True},
    )

    res2 = ToolResult(
        execution_id="e2",
        tool_name="sql_tool",
        status=ToolExecutionStatus.SUCCESS,
        execution_time_seconds=0.5,
        cost=0.005,
        compute_usage={"cpu_ms": 500.0, "memory_mb": 8.0},
    )

    tracker.track_execution(res1, ctx)
    tracker.track_execution(res2, ctx)

    summary = tracker.get_tenant_billing_summary("tenant_bill_1")
    assert summary["total_calls"] == 2
    assert summary["external_api_calls"] == 1
    assert summary["total_cost"] == 0.015
    assert summary["total_duration_seconds"] == 2.0
    assert summary["cpu_ms"] == 2000.0
    assert summary["bytes_read"] == 1024
    assert summary["tool_breakdown"]["http_tool"]["calls"] == 1
    assert summary["tool_breakdown"]["sql_tool"]["calls"] == 1
