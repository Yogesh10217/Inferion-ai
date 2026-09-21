"""
Tests for Python SDK Workflows Client
"""

from sdk.python.llm_engine.workflows import WorkflowClient


def test_sdk_workflow_client_interface():
    # Verify method signatures on WorkflowClient
    assert hasattr(WorkflowClient, "create")
    assert hasattr(WorkflowClient, "list")
    assert hasattr(WorkflowClient, "get")
    assert hasattr(WorkflowClient, "run")
    assert hasattr(WorkflowClient, "resume")
    assert hasattr(WorkflowClient, "approve")
    assert hasattr(WorkflowClient, "history")
    assert hasattr(WorkflowClient, "checkpoints")
    assert hasattr(WorkflowClient, "rollback")
    assert hasattr(WorkflowClient, "fork")
