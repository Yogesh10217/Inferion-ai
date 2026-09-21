"""Mandatory 20 End-to-End Integration Flow Tests for Operations Intelligence (Phase 5.41)."""

import pytest

from app.operations_intelligence.alerts import AlertSeverity, AlertStatus
from app.operations_intelligence.communications import CommunicationAudience
from app.operations_intelligence.correlation import CorrelationEvidence
from app.operations_intelligence.dependencies import DependencyImpact
from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    HighRiskOperationRequiresApprovalException,
    ImmutableOperationsRecordException,
    RemediationVerificationException,
)
from app.operations_intelligence.incidents import IncidentSeverity
from app.operations_intelligence.major_incidents import MajorIncidentImpact, MajorIncidentStatus
from app.operations_intelligence.manager import OperationsIntelligenceManager
from app.operations_intelligence.remediation import RemediationAction, RemediationStatus
from app.operations_intelligence.root_cause import RootCauseConfidence, RootCauseEvidence, RootCauseHypothesis


@pytest.fixture
def manager():
    return OperationsIntelligenceManager()


def test_flow1_operational_alert_ingestion(manager):
    """Flow 1 — Operational Alert Ingestion."""
    tenant_id = "tenant_a"
    svc = manager.service_manager.register_service(tenant_id, "API_Gateway", "NetworkTeam")
    alt = manager.alert_manager.ingest_alert(
        tenant_id=tenant_id,
        source_system="Prometheus",
        service_id=svc.service_id,
        alert_name="HighErrorRate",
        fingerprint="fp_api_gw_err_500",
        severity=AlertSeverity.HIGH,
    )

    assert alt.alert_id.startswith("alt_op_")
    assert alt.tenant_id == tenant_id
    assert alt.service_id == svc.service_id
    assert alt.duplicate_count == 1


def test_flow2_duplicate_alert_correlation(manager):
    """Flow 2 — Duplicate Alert Correlation."""
    tenant_id = "tenant_a"
    svc = manager.service_manager.register_service(tenant_id, "DB_Cluster", "DBATeam")
    fp = "fp_db_conn_timeout"

    alt1 = manager.alert_manager.ingest_alert(tenant_id, "Datadog", svc.service_id, "DBTimeout", fp)
    alt2 = manager.alert_manager.ingest_alert(tenant_id, "Datadog", svc.service_id, "DBTimeout", fp)

    assert alt1.alert_id == alt2.alert_id
    assert alt2.duplicate_count == 2
    assert alt2.status == AlertStatus.DEDUPLICATED


def test_flow3_incident_creation_from_correlated_alerts(manager):
    """Flow 3 — Incident Creation from Correlated Alerts."""
    tenant_id = "tenant_a"
    svc = manager.service_manager.register_service(tenant_id, "Auth_Service", "SecurityTeam")
    alt = manager.alert_manager.ingest_alert(tenant_id, "GuardDuty", svc.service_id, "AuthSpike", "fp_auth_spike")

    inc = manager.incident_manager.create_incident(
        tenant_id=tenant_id,
        title="Authentication Anomaly Detected",
        affected_service_id=svc.service_id,
        severity=IncidentSeverity.P1_CRITICAL,
    )

    ev = CorrelationEvidence(event_source="ALERTS", event_id=alt.alert_id, summary="Auth spike alert")
    corr = manager.correlation_manager.correlate_events(tenant_id, inc.incident_id, [ev])

    assert inc.incident_id.startswith("inc_op_")
    assert corr.primary_incident_id == inc.incident_id
    assert len(corr.correlated_events) == 1


def test_flow4_cross_service_dependency_impact_analysis(manager):
    """Flow 4 — Cross-Service Dependency Impact Analysis."""
    tenant_id = "tenant_a"
    manager.dependency_manager.add_dependency(tenant_id, "svc_auth", "svc_users", DependencyImpact.CRITICAL_PATH)
    manager.dependency_manager.add_dependency(tenant_id, "svc_users", "svc_billing", DependencyImpact.HIGH)

    analysis = manager.dependency_manager.analyze_failure_impact(tenant_id, "svc_auth")
    assert "svc_users" in analysis.impacted_services
    assert "svc_billing" in analysis.impacted_services


def test_flow5_major_incident_declaration(manager):
    """Flow 5 — Major Incident Declaration."""
    tenant_id = "tenant_a"
    inc = manager.incident_manager.create_incident(tenant_id, "Global Outage", "svc_core")
    maj = manager.major_incident_manager.declare_major_incident(
        tenant_id=tenant_id,
        incident_id=inc.incident_id,
        title="Global Outage Major Incident",
        impact=MajorIncidentImpact.CRITICAL_BUSINESS_HALT,
    )

    assert maj.major_incident_id.startswith("maj_inc_")
    assert maj.requires_human_oversight is True
    assert maj.status == MajorIncidentStatus.DECLARED


def test_flow6_root_cause_hypothesis_generation(manager):
    """Flow 6 — Root Cause Hypothesis Generation."""
    tenant_id = "tenant_a"
    hypo1 = RootCauseHypothesis(
        title="DB Connection Pool Exhaustion",
        component_name="Postgres",
        likelihood_score=85.0,
        reasoning="Connections capped at 100",
    )
    hypo2 = RootCauseHypothesis(
        title="Slow Query Lock", component_name="UserTable", likelihood_score=60.0, reasoning="Unindexed lookup"
    )

    rca = manager.root_cause_manager.analyze_root_cause(
        tenant_id=tenant_id,
        incident_id="inc_100",
        primary_root_cause="DB Connection Pool Exhaustion under high load",
        hypotheses=[hypo1, hypo2],
        evidence=[],
    )

    assert rca.analysis_id.startswith("rca_")
    assert len(rca.hypotheses) == 2
    assert rca.confidence == RootCauseConfidence.HIGH


def test_flow7_root_cause_evidence_validation(manager):
    """Flow 7 — Root Cause Evidence Validation."""
    tenant_id = "tenant_a"
    ev1 = RootCauseEvidence(source="PROMETHEUS_METRICS", description="Connection pool utilisation 100% at 14:02:11")
    ev2 = RootCauseEvidence(
        source="LOGS",
        description="FATAL: remaining connection slots reserved for non-replication superuser connections",
    )

    rca = manager.root_cause_manager.analyze_root_cause(
        tenant_id=tenant_id,
        incident_id="inc_200",
        primary_root_cause="Connection exhaustion",
        hypotheses=[],
        evidence=[ev1, ev2],
    )

    assert len(rca.evidence) == 2
    assert rca.evidence[0].source == "PROMETHEUS_METRICS"


def test_flow8_problem_creation(manager):
    """Flow 8 — Problem Creation."""
    tenant_id = "tenant_a"
    prob = manager.problem_manager.create_problem(tenant_id, "Recurring DB Pool Exhaustion", ["inc_100", "inc_200"])
    manager.problem_manager.set_root_cause(tenant_id, prob.problem_id, "rca_100")

    assert prob.problem_id.startswith("prob_op_")
    assert prob.status.value == "ROOT_CAUSE_IDENTIFIED"
    assert len(prob.associated_incident_ids) == 2


def test_flow9_known_error_recommendation(manager):
    """Flow 9 — Known Error Recommendation."""
    tenant_id = "tenant_a"
    prob = manager.problem_manager.create_problem(tenant_id, "Memory Leak Problem")
    ke = manager.known_error_manager.publish_known_error(
        tenant_id=tenant_id,
        title="Known Error: Worker Thread Leak",
        workaround="Restart worker node every 24 hours",
        problem_id=prob.problem_id,
    )

    assert ke.known_error_id.startswith("ke_op_")
    assert "Restart worker node" in ke.workaround


def test_flow10_high_risk_remediation_requires_approval(manager):
    """Flow 10 — High-Risk Remediation Requires Approval."""
    tenant_id = "tenant_a"
    action = RemediationAction(action_name="FAILOVER_PRIMARY_DB", target_service_id="svc_db", is_high_risk=True)
    plan = manager.remediation_manager.create_remediation_plan(
        tenant_id=tenant_id,
        incident_id="inc_300",
        idempotency_key="idem_failover_1",
        actions=[action],
        requires_approval=True,
    )

    with pytest.raises(HighRiskOperationRequiresApprovalException):
        manager.remediation_manager.delegate_remediation(tenant_id, plan.plan_id)

    # Approve and delegate successfully
    manager.remediation_manager.approve_remediation(tenant_id, plan.plan_id, "appr_db_failover")
    del_req = manager.remediation_manager.delegate_remediation(tenant_id, plan.plan_id)
    assert del_req.delegation_id.startswith("delreq_")


def test_flow11_delegation_only_remediation_enforcement(manager):
    """Flow 11 — Delegation-Only Remediation Enforcement (no direct infrastructure mutation)."""
    tenant_id = "tenant_a"
    action = RemediationAction(action_name="RESTART_SERVICE", target_service_id="svc_app", is_high_risk=False)
    plan = manager.remediation_manager.create_remediation_plan(tenant_id, "inc_400", "idem_restart_1", [action])

    del_req = manager.remediation_manager.delegate_remediation(tenant_id, plan.plan_id)
    assert del_req.payload["plan_id"] == plan.plan_id
    assert plan.status == RemediationStatus.DELEGATED


def test_flow12_idempotent_remediation_request(manager):
    """Flow 12 — Idempotent Remediation Request."""
    tenant_id = "tenant_a"
    action = RemediationAction(action_name="SCALE_UP", target_service_id="svc_app")
    plan1 = manager.remediation_manager.create_remediation_plan(tenant_id, "inc_500", "idem_unique_key_99", [action])
    plan2 = manager.remediation_manager.create_remediation_plan(tenant_id, "inc_500", "idem_unique_key_99", [action])

    assert plan1.plan_id == plan2.plan_id


def test_flow13_remediation_verification_failure(manager):
    """Flow 13 — Remediation Verification Failure."""
    tenant_id = "tenant_a"

    with pytest.raises(RemediationVerificationException) as exc_info:
        manager.verification_manager.verify_remediation(
            tenant_id, "rem_plan_100", service_recovered=False, notes="Health check endpoint timed out"
        )

    assert "rem_plan_100" in str(exc_info.value)


def test_flow14_cross_tenant_operational_access_blocked(manager):
    """Flow 14 — Cross-Tenant Operational Access Blocked with zero metadata leakage."""
    svc_a = manager.service_manager.register_service("tenant_a", "ServiceA", "TeamA")

    with pytest.raises(CrossTenantOperationsAccessException) as exc_info:
        manager.service_manager.get_service("tenant_b", svc_a.service_id)

    msg = str(exc_info.value)
    assert svc_a.service_id not in msg
    assert "tenant_a" not in msg
    assert "tenant_b" not in msg
    assert msg == "Access denied."


def test_flow15_sensitive_data_redaction(manager):
    """Flow 15 — Sensitive Data Redaction in Operational Communications."""
    tenant_id = "tenant_a"
    raw_msg = "Database password 'SecretPass123!' breached during deployment."
    comm = manager.communication_manager.create_communication(
        tenant_id=tenant_id,
        incident_id="inc_600",
        raw_message=raw_msg,
        audience=CommunicationAudience.INTERNAL_OPS,
    )

    assert "SecretPass123!" not in comm.sanitized_message


def test_flow16_immutable_incident_snapshot(manager):
    """Flow 16 — Immutable Incident Snapshot Generation."""
    tenant_id = "tenant_a"
    inv = manager.investigation_manager.open_investigation(tenant_id, "Failure Analysis", "inc_700")
    manager.investigation_manager.start_investigating(tenant_id, inv.investigation_id)
    manager.investigation_manager.record_finding(tenant_id, inv.investigation_id, "Root cause confirmed")

    concluded = manager.investigation_manager.conclude_investigation(tenant_id, inv.investigation_id)
    assert concluded.is_concluded is True
    assert concluded.snapshot_id is not None

    with pytest.raises(ImmutableOperationsRecordException):
        manager.investigation_manager.record_finding(tenant_id, inv.investigation_id, "Late finding")


def test_flow17_recurring_incident_learning_recommendation(manager):
    """Flow 17 — Recurring Incident Learning Recommendation (advisory only, auto_execute=False)."""
    tenant_id = "tenant_a"
    learning = manager.learning_manager.record_learning(
        tenant_id=tenant_id,
        pattern_name="RepeatedOOMPattern",
        description="OutOfMemory error observed 3 times in 24 hours",
        recommendation_title="Increase container memory limit",
        suggested_action="Set container memory request to 4GiB",
        target_service_id="svc_app",
    )

    rec = learning.recommendations[0]
    assert rec.auto_execute is False  # MUST be False!


def test_flow18_change_risk_correlation(manager):
    """Flow 18 — Change Risk Correlation."""
    tenant_id = "tenant_a"
    chg = manager.change_manager.register_change(tenant_id, "Upgrade Schema v2", "svc_db")
    risk_asm = manager.change_risk_manager.evaluate_change_risk(
        tenant_id=tenant_id,
        change_id=chg.change_id,
        affected_services_score=90.0,
        dependency_impact_score=85.0,
        is_emergency_change=True,
    )

    assert risk_asm.is_high_risk is True
    assert risk_asm.risk_level in ["CRITICAL", "HIGH"]


def test_flow19_major_incident_human_escalation(manager):
    """Flow 19 — Major Incident Human Escalation."""
    tenant_id = "tenant_a"
    maj = manager.major_incident_manager.declare_major_incident(tenant_id, "inc_800", "Critical Outage")

    with pytest.raises(HighRiskOperationRequiresApprovalException):
        manager.major_incident_manager.resolve_major_incident(tenant_id, maj.major_incident_id)

    # Approve human escalation
    manager.major_incident_manager.approve_major_incident_resolution(
        tenant_id, maj.major_incident_id, "appr_human_exec"
    )
    resolved_maj = manager.major_incident_manager.resolve_major_incident(tenant_id, maj.major_incident_id)
    assert resolved_maj.status == MajorIncidentStatus.RESOLVED


def test_flow20_full_enterprise_operations_lifecycle(manager):
    """Flow 20 — Full Enterprise Operations Intelligence Lifecycle."""
    tenant_id = "tenant_enterprise"
    result = manager.run_full_lifecycle(tenant_id, "EnterprisePaymentService", "PaymentGatewayOutage")

    assert result["status"] == "COMPLETED"
    assert result["service_id"].startswith("svc_op_")
    assert result["incident_id"].startswith("inc_op_")
    assert result["delegation_id"].startswith("delreq_")
    assert result["governance_status"] == "ALLOW"
    assert result["snapshot_id"].startswith("snap_op_")
    assert result["evidence_sha256"] != ""
    assert result["learning_auto_execute"] is False
