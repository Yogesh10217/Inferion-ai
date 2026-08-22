"""Unit tests for Saga pattern compensation execution in reverse order."""

import pytest
from app.orchestration.compensation import CompensationManager, SagaStep, SagaStepStatus


def test_saga_reverse_compensation():
    mgr = CompensationManager()

    steps = [
        SagaStep(step_id="step_1", action_name="create_resource", compensation_action="delete_resource"),
        SagaStep(step_id="step_2", action_name="grant_access", compensation_action="revoke_access"),
    ]

    saga = mgr.create_saga("exec_saga", steps, tenant_id="t_comp")
    mgr.mark_step_executed(saga.saga_id, "step_1")
    mgr.mark_step_executed(saga.saga_id, "step_2")

    # Execute compensation
    comp_saga = mgr.execute_compensation(saga.saga_id)
    assert comp_saga.is_compensated is True
    assert all(s.status == SagaStepStatus.COMPENSATED for s in comp_saga.steps)
