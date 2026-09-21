"""Unit tests for WorkflowKnowledgeAdapter integration."""

from app.knowledge_platform.workflow_integration import WorkflowKnowledgeAdapter


def test_workflow_knowledge_adapter():
    adapter = WorkflowKnowledgeAdapter()
    item_id = adapter.record_workflow_insight(
        "wf_100", title="Pipeline Benchmark", content="Passed 100%", tenant_id="t_wf_int"
    )
    assert item_id.startswith("kitem_")
