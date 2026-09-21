"""Unit tests for RunbookManager (DRY_RUN, EXECUTE, VERIFY, ROLLBACK)."""

from app.operations.runbooks import RunbookManager, RunbookMode, RunbookStep


def test_runbook_execution_modes():
    mgr = RunbookManager()

    step = RunbookStep(name="Invalidate Cache", action_type="INVALIDATE_CACHE", target_resource_id="redis_cluster")
    rb = mgr.create_runbook("Cache Reset Runbook", steps=[step], tenant_id="t_rb")

    # 1. DRY_RUN
    res_dry = mgr.execute_runbook(rb.runbook_id, mode=RunbookMode.DRY_RUN)
    assert res_dry.status == "DRY_RUN_PASSED"

    # 2. EXECUTE
    res_exec = mgr.execute_runbook(rb.runbook_id, mode=RunbookMode.EXECUTE)
    assert res_exec.status == "COMPLETED"

    # 3. VERIFY
    res_ver = mgr.execute_runbook(rb.runbook_id, mode=RunbookMode.VERIFY)
    assert res_ver.status == "VERIFIED"

    # 4. ROLLBACK
    res_roll = mgr.execute_runbook(rb.runbook_id, mode=RunbookMode.ROLLBACK)
    assert res_roll.status == "ROLLED_BACK"
