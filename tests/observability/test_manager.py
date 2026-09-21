"""Tests for ObservabilityManager workflow orchestration."""

from app.observability.manager import ObservabilityManager


def test_observability_manager_execution_flow():
    manager = ObservabilityManager()
    ctx = manager.create_context(
        trace_id="tr-mgr-1",
        execution_id="exec-mgr-1",
        tenant_id="tenant-mgr",
        agent_id="agent-mgr",
    )

    span_dict = manager.start_execution(component="agent", name="agent.execute", context=ctx)
    assert span_dict["trace_id"] == "tr-mgr-1"

    manager.end_execution(
        span_or_id=span_dict["span_id"],
        component="agent",
        status="OK",
        latency_ms=120.0,
        input_tokens=100,
        output_tokens=50,
        context=ctx,
    )

    timeline = manager.get_execution_timeline("tr-mgr-1")
    assert timeline["trace_id"] == "tr-mgr-1"
    assert timeline["total_tokens"] == 150

    status = manager.get_operations_status()
    assert status["status"] in ["HEALTHY", "DEGRADED"]
    assert "agent" in status["performance_summary"]
