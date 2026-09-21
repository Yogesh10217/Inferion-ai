"""Unit tests for compliance control gap detection."""

from app.governance_platform.compliance import ComplianceControl, ComplianceManager, ComplianceStatus, FrameworkType


def test_compliance_control_gap_detection():
    mgr = ComplianceManager()

    ctrls = [
        ComplianceControl(control_id="EU_AI_1", name="Risk Management System", status=ComplianceStatus.COMPLIANT),
        ComplianceControl(control_id="EU_AI_2", name="Technical Documentation", status=ComplianceStatus.NON_COMPLIANT),
    ]

    ass = mgr.run_assessment(FrameworkType.EU_AI_ACT, tenant_id="t_gap", controls=ctrls)
    assert ass.compliance_score_percent == 50.0
    assert ass.status == ComplianceStatus.PARTIALLY_COMPLIANT
    assert len(ass.findings) == 1
    assert "EU_AI_2" in ass.findings[0]
