"""
Tests for Restore Validation Engine.
"""

from app.reliability.restore_validation import RestoreStatus, RestoreValidationEngine


def test_restore_plan_validation():
    engine = RestoreValidationEngine()
    res = engine.validate_restore_plan()
    assert res.restore_status == RestoreStatus.READY
    assert res.backup_compatible is True
    assert res.production_database_restore_executed is False


def test_production_database_restore_remains_false():
    engine = RestoreValidationEngine()
    res = engine.validate_restore_plan(empirically_executed_on_production=False)
    assert res.production_database_restore_executed is False
