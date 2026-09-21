"""Unit tests for WorkflowDefinitionManager creation and lifecycle state."""

from app.orchestration.workflow import DefinitionLifecycleState, WorkflowDefinitionManager, WorkflowStep


def test_workflow_definition_creation_and_publishing():
    mgr = WorkflowDefinitionManager()
    steps = [WorkflowStep(step_id="s1", name="Step 1")]

    wf = mgr.create_definition("Onboarding Process", steps=steps, tenant_id="t_wf")
    assert wf.name == "Onboarding Process"
    assert wf.lifecycle_state == DefinitionLifecycleState.DRAFT

    # Publish
    pub_wf = mgr.publish_definition(wf.workflow_id)
    assert pub_wf.lifecycle_state == DefinitionLifecycleState.PUBLISHED
