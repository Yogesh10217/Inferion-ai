"""Unit tests for WorkflowGovernanceEngine pre-execution evaluation."""

from app.orchestration.governance import GovernanceAction, WorkflowGovernanceEngine


def test_workflow_governance_risk_evaluation():
    engine = WorkflowGovernanceEngine()

    # Standard execution -> ALLOW
    res_allow = engine.evaluate_workflow_execution("wf_1", action_name="read_data", risk_score=10.0)
    assert res_allow.governance_action == GovernanceAction.ALLOW

    # High risk / Production action -> REQUIRE_APPROVAL
    res_appr = engine.evaluate_workflow_execution("wf_1", action_name="production_deploy", risk_score=80.0)
    assert res_appr.governance_action == GovernanceAction.REQUIRE_APPROVAL
    assert res_appr.approval_request_id is not None
