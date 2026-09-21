"""Unit tests for strict multi-tenant isolation across governance entities."""

from app.governance_platform.compliance import ComplianceManager, FrameworkType
from app.governance_platform.evidence import EvidenceCollector, EvidenceSource
from app.governance_platform.risk import RiskCategory, RiskManager
from app.governance_platform.violations import ViolationManager, ViolationSeverity, ViolationType


def test_strict_multi_tenant_isolation():
    r_mgr = RiskManager()
    e_coll = EvidenceCollector()
    v_mgr = ViolationManager()
    c_mgr = ComplianceManager()

    # Tenant A
    r_mgr.calculate_risk("res_A", [], category=RiskCategory.SECURITY, tenant_id="Tenant_A")
    e_coll.collect_evidence(EvidenceSource.AUDIT_LOG, "rec_A", "res_A", {"data": "A"}, tenant_id="Tenant_A")
    v_mgr.record_violation(
        "Viol A", ViolationType.POLICY_VIOLATION, ViolationSeverity.LOW, "res_A", tenant_id="Tenant_A"
    )
    c_mgr.run_assessment(FrameworkType.SOC2, tenant_id="Tenant_A")

    # Tenant B
    r_mgr.calculate_risk("res_B", [], category=RiskCategory.SECURITY, tenant_id="Tenant_B")
    e_coll.collect_evidence(EvidenceSource.AUDIT_LOG, "rec_B", "res_B", {"data": "B"}, tenant_id="Tenant_B")
    v_mgr.record_violation(
        "Viol B", ViolationType.POLICY_VIOLATION, ViolationSeverity.LOW, "res_B", tenant_id="Tenant_B"
    )
    c_mgr.run_assessment(FrameworkType.SOC2, tenant_id="Tenant_B")

    # Verify zero data cross-leakage
    assert len(r_mgr.list_assessments("Tenant_A")) == 1
    assert len(r_mgr.list_assessments("Tenant_B")) == 1
    assert len(e_coll.list_evidence("Tenant_A")) == 1
    assert len(e_coll.list_evidence("Tenant_B")) == 1
    assert len(v_mgr.list_violations("Tenant_A")) == 1
    assert len(v_mgr.list_violations("Tenant_B")) == 1
    assert len(c_mgr.list_assessments("Tenant_A")) == 1
    assert len(c_mgr.list_assessments("Tenant_B")) == 1
