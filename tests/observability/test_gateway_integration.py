"""Integration tests for AI Gateway, Agent, Workflow, Tool, Team, Planning, and Autonomy subsystem telemetry."""

from app.observability.manager import ObservabilityManager


def test_gateway_telemetry_integration():
    om = ObservabilityManager()
    ctx = om.create_context(trace_id="tr-gw", model_id="gpt-4o", provider="openai")

    om.start_execution("gateway", "gateway.request", context=ctx)
    om.end_execution(
        "gateway.request", "gateway", status="OK", latency_ms=50.0, input_tokens=500, output_tokens=200, context=ctx
    )

    summary = om.performance.get_component_performance("gateway")
    assert summary.count == 1
    assert om.cost_tracker.get_cost_breakdown()["total_tokens"] == 700


def test_agent_telemetry_integration():
    om = ObservabilityManager()
    ctx = om.create_context(agent_id="agent-intel-1")

    om.start_execution("agent", "agent.execute", context=ctx)
    om.end_execution("agent.execute", "agent", status="OK", latency_ms=150.0, context=ctx)

    assert om.performance.get_component_performance("agent").count == 1


def test_workflow_telemetry_integration():
    om = ObservabilityManager()
    ctx = om.create_context(workflow_id="wf-flow-1")

    om.start_execution("workflow", "workflow.execute", context=ctx)
    om.end_execution("workflow.execute", "workflow", status="OK", latency_ms=300.0, context=ctx)

    assert om.performance.get_component_performance("workflow").count == 1


def test_tool_telemetry_integration():
    om = ObservabilityManager()
    ctx = om.create_context(tool_execution_id="tool-search")

    om.start_execution("tool", "tool.execute", context=ctx)
    om.end_execution("tool.execute", "tool", status="OK", latency_ms=80.0, context=ctx)

    assert om.performance.get_component_performance("tool").count == 1


def test_team_and_planning_telemetry_integration():
    om = ObservabilityManager()
    ctx = om.create_context(trace_id="tr-team-plan")

    om.start_execution("team", "team.execute", context=ctx)
    om.end_execution("team.execute", "team", status="OK", latency_ms=250.0, context=ctx)

    om.start_execution("planning", "planning.create", context=ctx)
    om.end_execution("planning.create", "planning", status="OK", latency_ms=120.0, context=ctx)

    assert om.performance.get_component_performance("team").count == 1
    assert om.performance.get_component_performance("planning").count == 1
