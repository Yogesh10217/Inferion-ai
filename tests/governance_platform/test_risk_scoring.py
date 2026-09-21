"""Unit tests for deterministic, reproducible risk scoring (0-100 scale)."""

from app.governance_platform.risk import RiskFactor, RiskManager, RiskSeverity


def test_deterministic_risk_scoring_and_evidence_breakdown():
    mgr = RiskManager()
    factors = [
        RiskFactor(name="PII Exposure", weight=2.0, impact_score=90.0, evidence_id="evd_1"),
        RiskFactor(name="Unrestricted External Tool", weight=1.0, impact_score=80.0, evidence_id="evd_2"),
    ]

    ass = mgr.calculate_risk("agent_worker_1", factors, tenant_id="t_score")

    # Weighted score = (90*2 + 80*1) / 3 = 260 / 3 = 86.666... -> CRITICAL
    assert round(ass.overall_score, 1) == 86.7
    assert ass.severity == RiskSeverity.CRITICAL
    assert "evd_1" in ass.evidence_ids
    assert "evd_2" in ass.evidence_ids
    assert ass.calculation_version == "1.0.0"
