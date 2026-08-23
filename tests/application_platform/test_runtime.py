"""Unit tests for Application Runtime Execution & Cancellation Token Propagation."""

import pytest
from app.application_platform.runtime import (
    ApplicationRuntimeManager,
    ApplicationRuntime,
    RuntimeState,
)
from app.application_platform.exceptions import ExecutionCancelledException, GovernanceBlockedException


def test_successful_runtime_pipeline_execution():
    rt_mgr = ApplicationRuntimeManager()
    ctx = rt_mgr.create_execution_context(
        tenant_id="t1",
        application_id="app_demo",
        application_version_id="ver_1",
    )

    runtime = ApplicationRuntime("app_demo", "t1")
    exec_result = runtime.execute_pipeline(ctx, {"message": "Hello Copilot"})

    assert exec_result.state == RuntimeState.COMPLETED
    assert "OUTPUT_SAFETY_CHECKED" in exec_result.steps_completed
    assert "response" in exec_result.output_payload


def test_runtime_cancellation_propagation():
    rt_mgr = ApplicationRuntimeManager()
    ctx = rt_mgr.create_execution_context(
        tenant_id="t1",
        application_id="app_demo",
        application_version_id="ver_1",
    )

    # Cancel execution prior to/during runtime step
    rt_mgr.cancel_execution(ctx.execution_id, reason="User cancelled request")

    runtime = ApplicationRuntime("app_demo", "t1")
    exec_result = runtime.execute_pipeline(ctx, {"message": "Long running query"})

    assert exec_result.state == RuntimeState.CANCELLED
    assert "User cancelled request" in exec_result.error
