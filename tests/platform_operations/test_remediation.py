"""Unit tests for Remediation Planning & Approval Risk Gating."""

import pytest
from app.platform_operations.remediation import RemediationPlanner, RemediationStep, RemediationStrategy, RemediationStatus
from app.platform_operations.exceptions import OperationalPolicyViolationException
from app.governance_platform.risk import RiskLevel


def test_high_risk_remediation_gated_by_approval():
    planner = RemediationPlanner()
    step = RemediationStep(
        strategy=RemediationStrategy.ROLLBACK,
        target_resource_id="svc_gateway",
        action_description="Rollback production gateway",
        expected_effect="Restore service",
        risk_level=RiskLevel.HIGH,
    )

    plan = planner.create_remediation_plan("t1", "inc_1", "svc_gateway", [step])
    assert plan.status == RemediationStatus.AWAITING_APPROVAL
    assert plan.approval_request_id is not None

    # Cannot execute before approval
    with pytest.raises(OperationalPolicyViolationException):
        planner.execute_remediation_plan(plan.plan_id, "t1")

    # Approve
    planner.approve_remediation_plan(plan.plan_id, approver_id="admin", tenant_id="t1")
    executed = planner.execute_remediation_plan(plan.plan_id, "t1")
    assert executed.status == RemediationStatus.SUCCESSFUL
