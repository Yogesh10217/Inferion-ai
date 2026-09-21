"""Unit tests for Automated Remediation Rollback on Execution/Verification Failure."""

from app.operations.remediation import AutonomousRemediationEngine, RemediationRisk, RemediationStatus
from app.operations.runbooks import RunbookManager, RunbookStep


def test_remediation_execution_failure_rollback():
    rb_mgr = RunbookManager()
    step = RunbookStep(name="Rollback Deployment", action_type="ROLLBACK_DEPLOYMENT", target_resource_id="deploy_9")
    rb = rb_mgr.create_runbook("Rollback Runbook", steps=[step], tenant_id="t_roll")

    engine = AutonomousRemediationEngine(runbook_manager=rb_mgr)
    plan = engine.plan_remediation(
        "Failed Remediation", "deploy_9", risk_level=RemediationRisk.LOW, runbook_id=rb.runbook_id, tenant_id="t_roll"
    )

    # Simulate execution failure -> triggers rollback
    exec_plan = engine.execute_remediation(plan.plan_id, simulate_failure=True)
    assert exec_plan.status == RemediationStatus.ROLLED_BACK
