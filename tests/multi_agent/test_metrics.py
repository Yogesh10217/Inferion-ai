"""
Tests for Multi-Agent Prometheus Metrics
"""

from app.multi_agent.agent_metrics import (
    agent_consensus_total,
    agent_delegations_total,
    agent_handoffs_total,
    agent_messages_total,
    agent_team_failures_total,
    agent_team_runs_total,
)


def test_agent_metrics_declarations():
    assert agent_team_runs_total._name == "agent_team_runs"
    assert agent_team_failures_total._name == "agent_team_failures"
    assert agent_messages_total._name == "agent_messages"
    assert agent_delegations_total._name == "agent_delegations"
    assert agent_consensus_total._name == "agent_consensus"


def test_agent_metrics_increment():
    agent_team_runs_total.labels(team_id="t1", team_type="engineering", tenant_id="tenant_1").inc()
    agent_messages_total.labels(message_type="TASK", team_id="t1").inc()
    agent_handoffs_total.labels(team_id="t1").inc()
