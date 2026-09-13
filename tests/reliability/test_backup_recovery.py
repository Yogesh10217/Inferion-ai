"""
Tests for Backup Recovery Module.
"""

from app.reliability.backup_recovery import BackupClassification, BackupRecoveryEvaluator


def test_backup_readiness_validation():
    evaluator = BackupRecoveryEvaluator()
    res = evaluator.evaluate_backup_readiness()
    assert res.classification == BackupClassification.READY
    assert res.rpo_compliant is True
    assert res.production_backup_executed is False


def test_backup_readiness_warning_on_rpo_exceeded():
    evaluator = BackupRecoveryEvaluator()
    res = evaluator.evaluate_backup_readiness(estimated_rpo_minutes=15.0, target_rpo_minutes=5.0)
    assert res.classification == BackupClassification.WARNING
    assert res.rpo_compliant is False
