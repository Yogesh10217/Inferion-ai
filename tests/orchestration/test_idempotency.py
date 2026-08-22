"""Unit tests for execution idempotency keys."""

import pytest
from app.orchestration.workflow import WorkflowDefinition, WorkflowStep
from app.orchestration.execution import WorkflowExecutionEngine


def test_idempotent_execution_start():
    engine = WorkflowExecutionEngine()
    wf_def = WorkflowDefinition(name="Idempotent WF", steps=[WorkflowStep(step_id="s1", name="S1")])

    exec1 = engine.start_execution(wf_def, idempotency_key="idemp_100")
    exec2 = engine.start_execution(wf_def, idempotency_key="idemp_100")

    assert exec1.execution_id == exec2.execution_id
