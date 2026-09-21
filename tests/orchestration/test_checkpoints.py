"""Unit tests for ExecutionCheckpoint persistence."""

from app.orchestration.execution import WorkflowExecutionEngine


def test_checkpoint_saving():
    engine = WorkflowExecutionEngine()

    chk = engine.save_checkpoint("exec_100", "step_2", {"processed": True}, tenant_id="t_chk")
    assert chk.execution_id == "exec_100"
    assert chk.step_id == "step_2"
    assert chk.state_data["processed"] is True
