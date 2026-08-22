"""Unit tests for Remediation Approval Gating (HIGH/CRITICAL risk require ApprovalEngine)."""

import pytest
from app.operations.remediation import AutonomousRemediationEngine, RemediationRisk, RemediationStatus
from app.operations.exceptions import RemediationFailedException


def test_high_risk_remediation_approval_gating():
    engine = AutonomousRemediationEngine()

    # HIGH risk plan -> APPROVAL_REQUIRED
    plan_high = engine.plan_remediation("Switch Provider to Anthropic", "provider_router", risk_level=RemediationRisk.HIGH, tenant_id="t_appr")
    assert plan_high.status == RemediationStatus.APPROVAL_REQUIRED
    assert plan_high.approval_request_id is not None

    # Direct execution without approval MUST fail!
    with pytest.raises(RemediationFailedException):
        engine.execute_remediation(plan_high.plan_id)

    # Approve plan
    engine.approve_remediation(plan_high.plan_id)
    assert engine.get_plan(plan_high.plan_id).status == RemediationStatus.APPROVED

    # Execution now succeeds
    exec_high = engine.execute_remediation(plan_high.plan_id)
    assert exec_high.status == RemediationStatus.COMPLETED
