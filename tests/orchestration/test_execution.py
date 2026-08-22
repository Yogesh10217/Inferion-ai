"""Unit tests for WorkflowExecutionEngine execution lifecycle."""

import pytest
from app.orchestration.workflow import WorkflowDefinition, WorkflowStep
from app.orchestration.execution import WorkflowExecutionEngine, WorkflowExecutionStatus


def test_workflow_execution_lifecycle():
    engine = WorkflowExecutionEngine()
    wf_def = WorkflowDefinition(name="Test Process", steps=[WorkflowStep(step_id="s1", name="S1")])

    exec_obj = engine.start_execution(wf_def, inputs={"data": 123}, tenant_id="t_exec")
    assert exec_obj.status == WorkflowExecutionStatus.RUNNING

    step_exec = engine.execute_step(exec_obj.execution_id, "s1", {"result": "ok"})
    assert step_exec.outputs["result"] == "ok"

    comp_exec = engine.complete_execution(exec_obj.execution_id, {"final": "success"})
    assert comp_exec.status == WorkflowExecutionStatus.COMPLETED
