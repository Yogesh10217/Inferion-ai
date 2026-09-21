"""Unit tests for ControlEnforcementEngine reversible actions."""

from app.governance_platform.remediation import ControlEnforcementEngine, EnforcementAction, RemediationStatus
from app.operations.remediation import RemediationRisk


def test_reversible_remediation_execution():
    engine = ControlEnforcementEngine()
    rem = engine.plan_remediation(
        "deploy_1", EnforcementAction.PAUSE_RESOURCE, risk_level=RemediationRisk.LOW, tenant_id="t_rem"
    )

    assert rem.status == RemediationStatus.APPROVED
    assert rem.is_reversible is True

    exec_rem = engine.execute_remediation(rem.remediation_id)
    assert exec_rem.status == RemediationStatus.COMPLETED
