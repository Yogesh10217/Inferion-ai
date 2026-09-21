"""Unit tests for workflow versioning."""

from app.orchestration.workflow import WorkflowDefinitionManager, WorkflowStep


def test_workflow_version_default():
    mgr = WorkflowDefinitionManager()
    steps = [WorkflowStep(step_id="s1", name="Step 1")]

    wf = mgr.create_definition("Versioned Process", steps=steps)
    assert wf.version == "1.0.0"
