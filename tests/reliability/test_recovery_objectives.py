"""
Tests for Recovery Objectives Module.
"""

from app.reliability.recovery_objectives import RecoveryObjectivesEvaluator


def test_rto_rpo_evaluation():
    evaluator = RecoveryObjectivesEvaluator()

    # Compliant case
    res = evaluator.evaluate_objectives(
        measured_rto_seconds=300.0,
        measured_rpo_seconds=120.0,
        measured_mttd_seconds=30.0,
        measured_mtta_seconds=180.0,
        measured_mttr_seconds=300.0,
    )
    assert res.rto_compliant is True
    assert res.rpo_compliant is True
    assert res.overall_compliant is True

    # Non-compliant RTO
    res_high_rto = evaluator.evaluate_objectives(
        measured_rto_seconds=1800.0,  # 30 mins > 15 mins target
        measured_rpo_seconds=120.0,
        measured_mttd_seconds=30.0,
        measured_mtta_seconds=180.0,
        measured_mttr_seconds=300.0,
    )
    assert res_high_rto.rto_compliant is False
    assert res_high_rto.overall_compliant is False
