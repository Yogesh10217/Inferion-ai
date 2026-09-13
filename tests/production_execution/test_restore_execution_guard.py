import pytest
from app.deployment.backup_execution_guard import BackupExecutionGuard
from app.deployment.models import BackupExecutionStatus


def test_restore_execution_guard_status():
    res = BackupExecutionGuard.evaluate_backup_guard(is_production=True, explicit_backup_authorized=True)
    assert res.restore_ready is True
    assert res.restore_status == BackupExecutionStatus.RESTORE_VALIDATED
