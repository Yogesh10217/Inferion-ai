import pytest
from app.deployment.backup_execution_guard import BackupExecutionGuard
from app.deployment.models import BackupExecutionStatus


def test_backup_execution_guard_planning():
    res = BackupExecutionGuard.evaluate_backup_guard(is_production=True, explicit_backup_authorized=False)
    assert res.backup_ready is True
    assert res.backup_status == BackupExecutionStatus.BACKUP_READY
    assert res.recovery_time_objective_minutes <= 15
    assert res.recovery_point_objective_minutes <= 5
