"""Tests for CostTracker and financial attribution hierarchy."""

from app.observability.context import ObservabilityContext
from app.observability.cost_tracking import CostTracker


def test_cost_calculation():
    tracker = CostTracker()
    cost = tracker.calculate_cost("gpt-4", "openai", input_tokens=1000, output_tokens=1000)
    assert cost == 0.09  # 0.03 + 0.06


def test_cost_recording_and_aggregations():
    tracker = CostTracker()
    ctx = ObservabilityContext(
        execution_id="exec-c1",
        tenant_id="ten-c1",
        workspace_id="ws-c1",
        organization_id="org-c1",
        agent_id="agent-c1",
    )

    tracker.record_usage(input_tokens=5000, output_tokens=2000, model="gpt-4o", context=ctx)
    tracker.record_usage(input_tokens=1000, output_tokens=1000, model="gpt-4o", context=ctx)

    exec_cost = tracker.get_execution_cost("exec-c1")
    assert exec_cost["input_tokens"] == 6000
    assert exec_cost["output_tokens"] == 3000
    assert exec_cost["records_count"] == 2

    agent_cost = tracker.get_agent_cost("agent-c1")
    assert agent_cost["records_count"] == 2

    breakdown = tracker.get_cost_breakdown(tenant_id="ten-c1")
    assert "org-c1" in breakdown["hierarchy"]
    assert "ten-c1" in breakdown["hierarchy"]["org-c1"]["tenants"]
