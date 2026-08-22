"""Unit tests for remediation approval gating on HIGH/CRITICAL risk."""

import pytest
from app.governance_platform.remediation import ControlEnforcementEngine, EnforcementAction, RemediationStatus
from app.governance_platform.exceptions import GovernancePlatformException
from app.operations.remediation import RemediationRisk


def test_high_risk_remediation_approval_requirement():
    engine = ControlEnforcementEngine()
    rem = engine.plan_remediation("deploy_prod", EnforcementAction.ROLLBACK_DEPLOYMENT, risk_level=RemediationRisk.HIGH, tenant_id="t_appr")

    assert rem.status == RemediationStatus.APPROVAL_REQUIRED
    assert rem.approval_request_id is not None

    # Direct execution without approval MUST raise exception!
    with pytest.raises(GovernancePlatformException):
        engine.execute_remediation(rem.remediation_id)

    # Approve remediation
    engine.approve_remediation(rem.remediation_id)
    assert engine.get_remediation(rem.remediation_id).status == RemediationStatus.APPROVED

    # Execution now succeeds
    exec_rem = engine.execute_remediation(rem.remediation_id)
    assert exec_rem.status == RemediationStatus.COMPLETED
