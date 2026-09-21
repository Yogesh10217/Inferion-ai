"""Unit tests for AgentKnowledgeAdapter integration."""

from app.knowledge_platform.agent_integration import AgentKnowledgeAdapter


def test_agent_knowledge_adapter():
    adapter = AgentKnowledgeAdapter()
    res = adapter.query_knowledge_for_agent("agent_1", query="financial report", tenant_id="t_ag_int")
    assert res.query == "financial report"
