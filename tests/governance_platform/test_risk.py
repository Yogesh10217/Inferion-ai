"""Unit tests for RiskManager assessment and lifecycle management."""

from app.governance_platform.risk import RiskCategory, RiskFactor, RiskManager, RiskSeverity, RiskStatus


def test_risk_identification_and_lifecycle():
    mgr = RiskManager()
    factors = [
        RiskFactor(name="Data Sensitivity", weight=1.0, impact_score=40.0),
        RiskFactor(name="Public Endpoint", weight=1.5, impact_score=50.0),
    ]

    ass = mgr.calculate_risk("res_api", factors, category=RiskCategory.SECURITY, tenant_id="t_risk")
    assert ass.overall_score == 46.0
    assert ass.severity == RiskSeverity.MEDIUM
    assert ass.status == RiskStatus.ASSESSED

    # Accept risk
    acc_ass = mgr.accept_risk(ass.assessment_id)
    assert acc_ass.status == RiskStatus.ACCEPTED
