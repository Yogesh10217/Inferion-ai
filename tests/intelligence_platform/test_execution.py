"""Unit tests for Delegation-Only Decision Execution Adapter."""

from app.intelligence_platform.execution import DecisionExecutionManager, ExecutionTarget
from app.intelligence_platform.recommendations import RecommendationManager, RecommendationType


def test_execution_delegation_boundary():
    rec_mgr = RecommendationManager()
    rec = rec_mgr.create_recommendation(
        "t1", RecommendationType.ROLLBACK_DEPLOYMENT, "Title", "Action", "svc_1", "Impact"
    )

    exec_mgr = DecisionExecutionManager()
    exec_res = exec_mgr.delegate_execution("t1", rec, ExecutionTarget.PLATFORM_OPERATIONS)

    assert exec_res.execution_id.startswith("exec_")
    assert exec_res.target == ExecutionTarget.PLATFORM_OPERATIONS
    assert exec_res.delegated_execution_ref is not None
