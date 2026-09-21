"""Mandatory End-to-End Governance Platform Integration Flow Verifications."""

from app.governance_platform.compliance import ComplianceControl, ComplianceStatus, FrameworkType
from app.governance_platform.evidence import EvidenceSource
from app.governance_platform.governance_manager import GovernancePlatformManager
from app.governance_platform.human_oversight import AutonomyLevel, OversightLevel
from app.governance_platform.remediation import EnforcementAction, RemediationStatus
from app.governance_platform.risk import RiskCategory, RiskFactor, RiskSeverity
from app.governance_platform.violations import ViolationSeverity, ViolationStatus, ViolationType
from app.operations.remediation import RemediationRisk


def test_flow_1_high_risk_agent_action_pipeline():
    mgr = GovernancePlatformManager()

    # 1. Policy evaluation for agent access to restricted dataset
    pol_res = mgr.policy_evaluator.evaluate_request(
        "access", "dataset_restricted_financial", tenant_id="f1", actor_id="agent_1", context={"is_data_access": True}
    )

    # 2. Risk manager calculates HIGH risk
    factors = [
        RiskFactor(name="Restricted Dataset Access", weight=2.0, impact_score=75.0),
        RiskFactor(name="External Agent Actor", weight=1.0, impact_score=60.0),
    ]
    risk_ass = mgr.risk_manager.calculate_risk(
        "dataset_restricted_financial", factors, category=RiskCategory.DATA, tenant_id="f1"
    )
    assert risk_ass.severity == RiskSeverity.HIGH

    # 3. Human oversight requires approval for high risk
    ovs_pol = mgr.human_oversight_engine.create_policy(
        "Agent Data Access Policy",
        "dataset_restricted_financial",
        AutonomyLevel.CONSTRAINED_AUTONOMOUS,
        OversightLevel.APPROVAL_REQUIRED,
        tenant_id="f1",
    )
    ovs_eval = mgr.human_oversight_engine.evaluate_action_autonomy(ovs_pol.policy_id, "access", is_restricted_data=True)

    assert ovs_eval["requires_approval"] is True

    # 4. Record evidence
    evd = mgr.evidence_collector.collect_evidence(
        EvidenceSource.POLICY_DECISION,
        pol_res.evaluation_id,
        "dataset_restricted_financial",
        pol_res.model_dump(),
        tenant_id="f1",
    )
    assert evd.content_hash != ""


def test_flow_2_model_safety_regression_pipeline():
    mgr = GovernancePlatformManager()

    # 1. MLOps safety regression detected by GovernanceMonitoringEngine
    mgr.monitoring_engine.run_monitoring_scan(tenant_id="f2", target_resource_id="model_gpt4_v2")

    # 2. Governance violation created + Operations Incident auto-created
    v = mgr.violation_manager.record_violation(
        title="Model Safety Evaluation Regression",
        violation_type=ViolationType.MODEL_SAFETY_VIOLATION,
        severity=ViolationSeverity.HIGH,
        primary_resource_id="model_gpt4_v2",
        description="Toxic outputs exceeded safety threshold in MLOps evaluation run",
        tenant_id="f2",
    )

    assert v.incident_id is not None  # Auto incident!

    # 3. Remediation recommendation: Block Deployment
    rem = mgr.enforcement_engine.plan_remediation(
        "model_gpt4_v2", EnforcementAction.BLOCK_DEPLOYMENT, risk_level=RemediationRisk.LOW, tenant_id="f2"
    )
    exec_rem = mgr.enforcement_engine.execute_remediation(rem.remediation_id)

    assert exec_rem.status == RemediationStatus.COMPLETED


def test_flow_3_critical_data_violation_containment():
    mgr = GovernancePlatformManager()

    # 1. Critical violation detected
    v = mgr.violation_manager.record_violation(
        title="Unauthorized Sensitive Data Exfiltration Attempt",
        violation_type=ViolationType.DATA_VIOLATION,
        severity=ViolationSeverity.CRITICAL,
        primary_resource_id="dataset_customer_pii",
        tenant_id="f3",
    )

    # 2. Automatic reversible containment (temporary access revocation)
    rem = mgr.enforcement_engine.plan_remediation(
        "dataset_customer_pii",
        EnforcementAction.REVOKE_ACCESS,
        risk_level=RemediationRisk.CRITICAL,
        is_emergency=True,
        tenant_id="f3",
    )
    assert rem.is_reversible is True

    exec_rem = mgr.enforcement_engine.execute_remediation(rem.remediation_id)
    assert exec_rem.status == RemediationStatus.COMPLETED

    # 3. Evidence preserved
    evd = mgr.evidence_collector.collect_evidence(
        EvidenceSource.INCIDENT, v.incident_id or "inc_1", "dataset_customer_pii", v.model_dump(), tenant_id="f3"
    )
    assert evd.content_hash != ""


def test_flow_4_compliance_evidence_assessment():
    mgr = GovernancePlatformManager()

    # 1. Evidence collected across systems
    e1 = mgr.evidence_collector.collect_evidence(
        EvidenceSource.AUDIT_LOG, "rec_1", "res_1", {"action": "LOGIN"}, tenant_id="f4"
    )
    e2 = mgr.evidence_collector.collect_evidence(
        EvidenceSource.DEPLOYMENT, "dep_1", "res_1", {"action": "DEPLOY"}, tenant_id="f4"
    )

    # 2. Controls mapped & framework assessed
    ctrls = [
        ComplianceControl(
            control_id="CC1.1", name="Audit Evidence", status=ComplianceStatus.COMPLIANT, evidence_ids=[e1.evidence_id]
        ),
        ComplianceControl(
            control_id="CC2.1",
            name="Deployment Gating",
            status=ComplianceStatus.COMPLIANT,
            evidence_ids=[e2.evidence_id],
        ),
    ]
    ass = mgr.compliance_manager.run_assessment(FrameworkType.SOC2, tenant_id="f4", controls=ctrls)

    assert ass.compliance_score_percent == 100.0
    assert ass.status == ComplianceStatus.COMPLIANT

    # 3. Audit package generated
    pkg = mgr.report_generator.generate_audit_package(tenant_id="f4")
    assert pkg.tenant_id == "f4"


def test_flow_5_autonomous_agent_boundary():
    mgr = GovernancePlatformManager()

    # 1. Create autonomy policy for constrained agent
    pol = mgr.human_oversight_engine.create_policy(
        "Constrained Agent Policy",
        "agent_worker_x",
        AutonomyLevel.CONSTRAINED_AUTONOMOUS,
        config_modification_allowed=False,
        tenant_id="f5",
    )

    # 2. Agent attempts privileged config modification
    res = mgr.human_oversight_engine.evaluate_action_autonomy(
        pol.policy_id, "modify_prod_config", is_config_change=True
    )

    assert res["allowed"] is False
    assert res["requires_approval"] is True

    # 3. Violation recorded & explanation generated
    v = mgr.violation_manager.record_violation(
        "Autonomy Boundary Breach Attempt",
        ViolationType.AUTONOMY_VIOLATION,
        ViolationSeverity.MEDIUM,
        "agent_worker_x",
        tenant_id="f5",
    )
    assert v.status == ViolationStatus.DETECTED


def test_flow_6_high_risk_remediation():
    mgr = GovernancePlatformManager()

    # 1. Governance violation requires deployment rollback (Risk = HIGH)
    rem = mgr.enforcement_engine.plan_remediation(
        "deploy_prod_v3", EnforcementAction.ROLLBACK_DEPLOYMENT, risk_level=RemediationRisk.HIGH, tenant_id="f6"
    )
    assert rem.status == RemediationStatus.APPROVAL_REQUIRED

    # 2. Administrator approves via ApprovalEngine
    mgr.enforcement_engine.approve_remediation(rem.remediation_id)

    # 3. Execution succeeds post-approval
    exec_rem = mgr.enforcement_engine.execute_remediation(rem.remediation_id)
    assert exec_rem.status == RemediationStatus.COMPLETED


def test_flow_7_tenant_isolation_verification():
    mgr = GovernancePlatformManager()

    # Tenant A governance data
    mgr.risk_manager.calculate_risk("res_A", [], category=RiskCategory.SECURITY, tenant_id="Tenant_A")
    mgr.evidence_collector.collect_evidence(
        EvidenceSource.AUDIT_LOG, "rec_A", "res_A", {"data": "A"}, tenant_id="Tenant_A"
    )
    mgr.violation_manager.record_violation(
        "Viol A", ViolationType.POLICY_VIOLATION, ViolationSeverity.LOW, "res_A", tenant_id="Tenant_A"
    )
    mgr.compliance_manager.run_assessment(FrameworkType.SOC2, tenant_id="Tenant_A")

    # Tenant B governance data
    mgr.risk_manager.calculate_risk("res_B", [], category=RiskCategory.SECURITY, tenant_id="Tenant_B")
    mgr.evidence_collector.collect_evidence(
        EvidenceSource.AUDIT_LOG, "rec_B", "res_B", {"data": "B"}, tenant_id="Tenant_B"
    )
    mgr.violation_manager.record_violation(
        "Viol B", ViolationType.POLICY_VIOLATION, ViolationSeverity.LOW, "res_B", tenant_id="Tenant_B"
    )
    mgr.compliance_manager.run_assessment(FrameworkType.SOC2, tenant_id="Tenant_B")

    # Verify zero cross-tenant leakage
    assert len(mgr.risk_manager.list_assessments("Tenant_A")) == 1
    assert len(mgr.risk_manager.list_assessments("Tenant_B")) == 1
    assert len(mgr.evidence_collector.list_evidence("Tenant_A")) == 1
    assert len(mgr.evidence_collector.list_evidence("Tenant_B")) == 1
    assert len(mgr.violation_manager.list_violations("Tenant_A")) == 1
    assert len(mgr.violation_manager.list_violations("Tenant_B")) == 1
    assert len(mgr.compliance_manager.list_assessments("Tenant_A")) == 1
    assert len(mgr.compliance_manager.list_assessments("Tenant_B")) == 1
