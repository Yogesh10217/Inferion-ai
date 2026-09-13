from __future__ import annotations

import pytest
from app.deployment.disaster_recovery import BackupReadinessEvaluator, DisasterRecoveryPlan, RecoveryObjective


def test_disaster_recovery_plan_objectives():
    dr_plan = DisasterRecoveryPlan()

    assert dr_plan.recovery_objective.recovery_time_objective_minutes == 15
    assert dr_plan.recovery_objective.recovery_point_objective_minutes == 5
    assert dr_plan.restore_validation.automated_integrity_check is True
    assert dr_plan.execution_status == "NOT_EXECUTED"


def test_disaster_recovery_evaluation():
    res = BackupReadinessEvaluator.evaluate_disaster_recovery_readiness(is_production=False)

    assert res.status == "READY"
    assert "DISASTER_RECOVERY_READINESS_EVALUATED" in res.classifications
    assert "PRODUCTION_RESTORE_EXECUTED = NOT_EXECUTED" in res.classifications
