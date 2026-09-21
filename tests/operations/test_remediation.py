"""Unit tests for AutonomousRemediationEngine lifecycle and approval gating."""

from app.operations.remediation import AutonomousRemediationEngine, RemediationRisk, RemediationStatus


def test_autonomous_remediation_low_and_medium_risk():
    engine = AutonomousRemediationEngine()

    # LOW risk -> Auto-approved
    plan_low = engine.plan_remediation(
        "Scale Workers", "worker_pool_1", risk_level=RemediationRisk.LOW, tenant_id="t_rem"
    )
    assert plan_low.status == RemediationStatus.APPROVED

    exec_low = engine.execute_remediation(plan_low.plan_id)
    assert exec_low.status == RemediationStatus.COMPLETED
    assert exec_low.verification_passed is True
