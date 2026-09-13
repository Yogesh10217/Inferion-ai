from __future__ import annotations

import pytest
from app.deployment.disaster_recovery import BackupReadinessEvaluator


def test_backup_readiness_planning():
    res = BackupReadinessEvaluator.evaluate_disaster_recovery_readiness(is_production=True)

    assert res.status == "READY"
    assert res.dr_plan.backup_strategy_defined is True
    assert res.dr_plan.restore_strategy_defined is True
    assert "BACKUP_READINESS_EVALUATED" in res.classifications
    assert "PRODUCTION_BACKUP_EXECUTED = NOT_EXECUTED" in res.classifications
