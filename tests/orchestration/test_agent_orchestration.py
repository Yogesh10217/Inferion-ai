"""Unit tests for AgentOrchestrationManager execution."""

import pytest
from app.orchestration.agent_orchestration import AgentOrchestrationManager, AgentTask


def test_agent_orchestration_execution():
    mgr = AgentOrchestrationManager()

    task = AgentTask(agent_id="agent_1", action="analyze_report", tenant_id="t_ag_orch")
    res = mgr.execute_agent_task(task, requested_scope="read")

    assert res["status"] == "SUCCESS"
    assert res["agent_id"] == "agent_1"
