"""Mandatory End-to-End Operations Integration Flow Verifications."""

from app.operations.alerting import AlertSeverity
from app.operations.incidents import IncidentSeverity, IncidentStatus
from app.operations.manager import OperationsManager
from app.operations.remediation import RemediationRisk, RemediationStatus
from app.operations.telemetry import TelemetryContext, TelemetryType


def test_flow_1_dependency_failure_pipeline():
    mgr = OperationsManager()

    # 1. Register topology nodes
    mgr.topology_manager.register_node("db_primary", "Database", "DATABASE", tenant_id="f1")
    mgr.topology_manager.register_node("api_gateway", "API Gateway", "GATEWAY", tenant_id="f1")
    mgr.topology_manager.add_dependency("api_gateway", "db_primary", "HARD", tenant_id="f1")

    # 2. Database degradation -> Health update
    mgr.topology_manager.update_node_health("db_primary", "UNHEALTHY")

    # 3. SLO burn increases -> Measurement
    slo = mgr.slo_manager.create_slo("DB Availability", 99.9, tenant_id="f1")
    mgr.slo_manager.record_measurement(slo.slo_id, 95.0)  # Breached!

    # 4. Alert generated
    alt = mgr.alert_manager.trigger_alert(
        "DBDegraded", "db_primary", "Database health critical", tenant_id="f1", severity=AlertSeverity.CRITICAL
    )

    # 5. Incident created
    inc = mgr.incident_manager.create_incident(
        "DB Failure Cascade",
        tenant_id="f1",
        severity=IncidentSeverity.SEV1_CRITICAL,
        primary_resource_id="db_primary",
        alert_ids=[alt.alert_id],
    )

    # 6. Topology impact analysis & Root Cause candidate
    rca = mgr.rca_engine.analyze_incident(inc.incident_id, "db_primary", tenant_id="f1")

    assert inc.status == IncidentStatus.DETECTED
    assert len(rca.candidates) >= 1
    assert rca.candidates[0].resource_id == "db_primary"


def test_flow_2_deployment_regression_and_rollback():
    mgr = OperationsManager()

    # 1. New deployment change recorded
    mgr.change_engine.record_change("DEPLOYMENT", "deploy_v2", "Deploy v2 model gateway", tenant_id="f2")

    # 2. Incident created
    mgr.incident_manager.create_incident(
        "Post-Deploy Error Surge", tenant_id="f2", severity=IncidentSeverity.SEV2_HIGH, primary_resource_id="deploy_v2"
    )

    # 3. Change correlation identifies deployment
    recent = mgr.change_engine.find_recent_changes("f2", "deploy_v2")
    assert len(recent) == 1

    # 4. Remediation plan & Rollback
    plan = mgr.remediation_engine.plan_remediation(
        "Rollback v2 Deployment", "deploy_v2", risk_level=RemediationRisk.LOW, tenant_id="f2"
    )
    exec_plan = mgr.remediation_engine.execute_remediation(plan.plan_id)

    assert exec_plan.status == RemediationStatus.COMPLETED
    assert exec_plan.verification_passed is True


def test_flow_3_autonomous_low_risk_remediation():
    mgr = OperationsManager()

    # 1. Capacity risk detected
    pred = mgr.prediction_engine.predict_capacity_risk(
        "f3", "worker_pool_alpha", current_queue_depth=90, max_capacity=100
    )
    assert pred is not None

    # 2. Remediation plan
    plan = mgr.remediation_engine.plan_remediation(
        "Scale Worker Concurrency", "worker_pool_alpha", risk_level=RemediationRisk.LOW, tenant_id="f3"
    )
    assert plan.status == RemediationStatus.APPROVED  # Auto approved!

    # 3. Automatic execution and health verification
    exec_plan = mgr.remediation_engine.execute_remediation(plan.plan_id)
    assert exec_plan.status == RemediationStatus.COMPLETED


def test_flow_4_high_risk_remediation_approval_gate():
    mgr = OperationsManager()

    # 1. Production model degradation -> Recommendation
    plan = mgr.remediation_engine.plan_remediation(
        "Switch Model Provider to Fallback", "llm_router", risk_level=RemediationRisk.HIGH, tenant_id="f4"
    )

    # 2. Risk = HIGH -> Requires ApprovalEngine!
    assert plan.status == RemediationStatus.APPROVAL_REQUIRED
    assert plan.approval_request_id is not None

    # 3. Administrator approves
    mgr.remediation_engine.approve_remediation(plan.plan_id)

    # 4. Execution succeeds after approval
    exec_plan = mgr.remediation_engine.execute_remediation(plan.plan_id)
    assert exec_plan.status == RemediationStatus.COMPLETED


def test_flow_5_root_cause_correlation():
    mgr = OperationsManager()
    mgr.topology_manager.register_node("cache_cluster", "Redis Cache", "CACHE", tenant_id="f5")
    mgr.topology_manager.register_node("search_service", "Search Service", "SERVICE", tenant_id="f5")
    mgr.topology_manager.add_dependency("search_service", "cache_cluster", "HARD", tenant_id="f5")

    mgr.topology_manager.update_node_health("cache_cluster", "DEGRADED")
    mgr.change_engine.record_change("CONFIG_CHANGE", "cache_cluster", "Updated eviction policy", tenant_id="f5")

    inc = mgr.incident_manager.create_incident(
        "Search Latency Spike", tenant_id="f5", primary_resource_id="cache_cluster"
    )
    recent = mgr.change_engine.find_recent_changes("f5", "cache_cluster")

    rca = mgr.rca_engine.analyze_incident(
        inc.incident_id, "cache_cluster", recent_changes=[c.model_dump() for c in recent], tenant_id="f5"
    )

    assert len(rca.candidates) >= 1
    assert rca.primary_cause_id is not None


def test_flow_6_strict_tenant_isolation_verification():
    mgr = OperationsManager()

    # Tenant A data
    mgr.telemetry_manager.record_event("gw", TelemetryType.LOG, "Log A", context=TelemetryContext(tenant_id="Tenant_A"))
    mgr.slo_manager.create_slo("SLO A", 99.9, tenant_id="Tenant_A")
    mgr.alert_manager.trigger_alert("Rule A", "gw", "Alert A", tenant_id="Tenant_A")
    mgr.incident_manager.create_incident("Incident A", tenant_id="Tenant_A")

    # Tenant B data
    mgr.telemetry_manager.record_event("gw", TelemetryType.LOG, "Log B", context=TelemetryContext(tenant_id="Tenant_B"))
    mgr.slo_manager.create_slo("SLO B", 99.0, tenant_id="Tenant_B")
    mgr.alert_manager.trigger_alert("Rule B", "gw", "Alert B", tenant_id="Tenant_B")
    mgr.incident_manager.create_incident("Incident B", tenant_id="Tenant_B")

    # Verify zero data leakage across tenants
    assert len(mgr.telemetry_manager.list_events("Tenant_A")) == 1
    assert len(mgr.telemetry_manager.list_events("Tenant_B")) == 1
    assert len(mgr.slo_manager.list_slos("Tenant_A")) == 1
    assert len(mgr.slo_manager.list_slos("Tenant_B")) == 1
    assert len(mgr.alert_manager.list_alerts("Tenant_A")) == 1
    assert len(mgr.alert_manager.list_alerts("Tenant_B")) == 1
    assert len(mgr.incident_manager.list_incidents("Tenant_A")) == 1
    assert len(mgr.incident_manager.list_incidents("Tenant_B")) == 1
