"""Unit tests for ComplianceManager assessments and legal disclaimer verification."""

from app.governance_platform.compliance import ComplianceManager, FrameworkType


def test_compliance_assessment_and_disclaimer():
    mgr = ComplianceManager()
    ass = mgr.run_assessment(FrameworkType.SOC2, tenant_id="t_comp")

    assert ass.framework == FrameworkType.SOC2
    assert ass.compliance_score_percent >= 0.0
    assert "does NOT constitute legal certification" in ass.disclaimer
