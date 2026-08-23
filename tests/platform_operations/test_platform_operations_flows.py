"""Mandatory End-to-End Integration Flows for Platform Operations Platform."""

import pytest
from datetime import datetime, timezone

from app.platform_operations.manager import PlatformOperationsManager
from app.platform_operations.services import ServiceTier, ServiceHealth
from app.platform_operations.signals import SignalSource, SignalType, SignalSeverity
from app.platform_operations.anomalies import AnomalyType
from app.platform_operations.remediation import RemediationStep, RemediationStrategy, RemediationStatus
from app.platform_operations.autonomous_operations import AutonomyLevel
from app.platform_operations.exceptions import RemediationPlanException, ServiceNotFoundException, OperationalPolicyViolationException
from app.governance_platform.risk import RiskLevel


def test_e2e_flow_1_deployment_regression():
    """FLOW 1 — Deployment Regression: Deployment -> latency surge -> signal correlation -> anomaly -> diagnosis -> rollback -> verification -> learning."""
    mgr = PlatformOperationsManager()
    tenant = "t_flow1"

    # 1. Register service & record deployment change
    svc = mgr.service_catalog_manager.register_service(tenant, "Checkout API", ServiceTier.TIER_1_HIGH)
    mgr.change_intelligence_engine.record_change(tenant, "DEPLOYMENT", svc.service_id, "v2.1.0")

    # 2. Ingest deployment event and error signals
    mgr.signal_manager.ingest_signal(tenant, SignalSource.DEPLOYMENT, SignalType.DEPLOYMENT_EVENT, "Deployed v2.1.0", service_id=svc.service_id)
    sig_err = mgr.signal_manager.ingest_signal(tenant, SignalSource.APPLICATION_RUNTIME, SignalType.RUNTIME_DEGRADATION, "Latency spike >3000ms", severity=SignalSeverity.CRITICAL, service_id=svc.service_id, metrics={"latency_ms": 3200.0})

    # 3. Detect anomaly & correlate signals
    signals = mgr.signal_manager.list_signals(tenant, service_id=svc.service_id)
    anomalies = mgr.anomaly_detector.detect_anomalies(tenant, signals)
    assert len(anomalies) >= 1

    # 4. Incident context & diagnosis
    ctx = mgr.incident_intelligence_engine.create_and_enrich_incident(
        tenant_id=tenant,
        title="Post-Deployment Latency Surge",
        primary_resource_id=svc.service_id,
        signals=signals,
        anomalies=anomalies,
        recent_deployments=[{"version_id": "v2.1.0"}],
    )
    diag = mgr.root_cause_analyzer.diagnose_incident(tenant, ctx)
    assert diag.top_hypothesis is not None
    assert diag.top_hypothesis.category == "DEPLOYMENT_REGRESSION"

    # 5. Remediation plan & execution
    step = RemediationStep(strategy=RemediationStrategy.ROLLBACK, target_resource_id=svc.service_id, action_description="Rollback to v2.0.9", expected_effect="Restore low latency", risk_level=RiskLevel.MEDIUM)
    plan = mgr.remediation_planner.create_remediation_plan(tenant, ctx.incident_id, svc.service_id, [step])
    executed = mgr.remediation_planner.execute_remediation_plan(plan.plan_id, tenant)
    assert executed.status == RemediationStatus.SUCCESSFUL

    # 6. Verification
    verif = mgr.remediation_verifier.verify_remediation(tenant, plan.plan_id)
    assert verif.is_verified is True

    # 7. Post-Incident Learning
    insight = mgr.operational_learning_manager.generate_post_incident_insight(tenant, ctx.incident_id, "v2.1.0 Deployment Regression", "Latency surge resolved by rollback", "Memory leak in v2.1.0 connection pool")
    assert insight.insight_id.startswith("ins_")


def test_e2e_flow_2_autonomous_safe_recovery():
    """FLOW 2 — Autonomous Safe Recovery: Transient failure -> constrained autonomous retry -> recovery -> audit."""
    mgr = PlatformOperationsManager()
    tenant = "t_flow2"

    svc = mgr.service_catalog_manager.register_service(tenant, "Transient Worker", ServiceTier.TIER_2_MEDIUM)
    sig = mgr.signal_manager.ingest_signal(tenant, SignalSource.WORKFLOW, SignalType.WORKFLOW_FAILURE, "Transient timeout contacting worker", service_id=svc.service_id)

    step = RemediationStep(strategy=RemediationStrategy.RETRY, target_resource_id=svc.service_id, action_description="Retry worker task", expected_effect="Recovery", risk_level=RiskLevel.LOW)
    plan = mgr.remediation_planner.create_remediation_plan(tenant, "inc_transient", svc.service_id, [step])

    auto_op = mgr.autonomous_operations_engine.execute_autonomous_remediation(tenant, plan.plan_id, autonomy_level=AutonomyLevel.CONSTRAINED_AUTONOMOUS)
    assert auto_op.status == "SUCCESSFUL"


def test_e2e_flow_3_high_risk_production_remediation():
    """FLOW 3 — High-Risk Production Remediation: Critical issue -> HIGH risk plan -> RiskManager & ApprovalEngine -> admin approval -> workflow execution -> verification."""
    mgr = PlatformOperationsManager()
    tenant = "t_flow3"

    svc = mgr.service_catalog_manager.register_service(tenant, "Core Banking Engine", ServiceTier.TIER_0_CRITICAL)
    step = RemediationStep(strategy=RemediationStrategy.FAILOVER, target_resource_id=svc.service_id, action_description="Failover primary region", expected_effect="Restore core banking", risk_level=RiskLevel.HIGH)
    plan = mgr.remediation_planner.create_remediation_plan(tenant, "inc_banking_down", svc.service_id, [step])

    assert plan.status == RemediationStatus.AWAITING_APPROVAL

    # Approval required before execution
    with pytest.raises(OperationalPolicyViolationException):
        mgr.remediation_planner.execute_remediation_plan(plan.plan_id, tenant)

    # Approve
    mgr.remediation_planner.approve_remediation_plan(plan.plan_id, approver_id="admin", tenant_id=tenant)
    executed = mgr.remediation_planner.execute_remediation_plan(plan.plan_id, tenant)
    assert executed.status == RemediationStatus.SUCCESSFUL


def test_e2e_flow_4_failed_remediation_rollback():
    """FLOW 4 — Failed Remediation Rollback: Remediation executed -> verification fails -> automatic rollback/compensation triggered."""
    mgr = PlatformOperationsManager()
    tenant = "t_flow4"

    svc = mgr.service_catalog_manager.register_service(tenant, "Broken Microservice", ServiceTier.TIER_1_HIGH)
    mgr.service_catalog_manager.update_service_health(svc.service_id, tenant, ServiceHealth.UNHEALTHY)

    step = RemediationStep(strategy=RemediationStrategy.RESTART, target_resource_id=svc.service_id, action_description="Restart service", expected_effect="Health recovery", risk_level=RiskLevel.LOW)
    plan = mgr.remediation_planner.create_remediation_plan(tenant, "inc_broken", svc.service_id, [step])
    mgr.remediation_planner.execute_remediation_plan(plan.plan_id, tenant)

    # Verification fails because service is still UNHEALTHY -> triggers automatic rollback
    verif = mgr.remediation_verifier.verify_remediation(tenant, plan.plan_id, auto_rollback_on_failure=True)
    assert verif.is_verified is False
    assert verif.is_rolled_back is True
    assert mgr.remediation_planner.get_plan(plan.plan_id, tenant).status == RemediationStatus.ROLLED_BACK


def test_e2e_flow_5_change_correlation():
    """FLOW 5 — Change Correlation: Config change -> incident occurs -> change correlation identifies suspected change."""
    mgr = PlatformOperationsManager()
    tenant = "t_flow5"

    svc = mgr.service_catalog_manager.register_service(tenant, "Search Indexer", ServiceTier.TIER_2_MEDIUM)
    chg = mgr.change_intelligence_engine.record_change(tenant, "CONFIG_CHANGE", svc.service_id, "batch_size=10000")

    now = datetime.now(timezone.utc)
    correlations = mgr.change_intelligence_engine.correlate_incident_with_changes(tenant, "inc_search_slow", now, [svc.service_id])

    assert len(correlations) >= 1
    assert correlations[0].suspected_change.change_id == chg.change_id


def test_e2e_flow_6_capacity_risk():
    """FLOW 6 — Capacity Risk: Queue backlog grows -> capacity risk -> scale recommendation -> FinOps cost tracking."""
    mgr = PlatformOperationsManager()
    tenant = "t_flow6"

    svc = mgr.service_catalog_manager.register_service(tenant, "Document Processing Queue", ServiceTier.TIER_1_HIGH)
    assessment = mgr.capacity_manager.assess_service_capacity(tenant, svc.service_id, cpu_utilization_pct=92.0, queue_backlog_count=850)

    assert assessment.risk.value in ("HIGH", "CRITICAL")
    assert assessment.recommendation == "SCALE_UP"

    # FinOps billing attribution for scaling action
    cost_evt = mgr.billing_tracker.record_operation_cost(tenant, svc.service_id, "SCALING", amount_usd=25.0)
    assert cost_evt.amount_usd == 25.0


def test_e2e_flow_7_post_incident_learning():
    """FLOW 7 — Post-Incident Learning: Resolved incident -> post-incident insight -> knowledge item stored with provenance."""
    mgr = PlatformOperationsManager()
    tenant = "t_flow7"

    insight = mgr.operational_learning_manager.generate_post_incident_insight(
        tenant_id=tenant,
        incident_id="inc_redis_timeout",
        title="Redis Cluster Timeout Under Heavy Load",
        summary="Redis pool size exhausted",
        root_cause_summary="Connection pool max size too small for concurrent tasks",
    )
    assert insight.title == "Redis Cluster Timeout Under Heavy Load"
    assert len(mgr.operational_learning_manager.list_insights(tenant)) >= 1


def test_e2e_flow_8_strict_cross_tenant_isolation():
    """FLOW 8 — Strict Cross-Tenant Isolation: Tenant A resources inaccessible to Tenant B."""
    mgr = PlatformOperationsManager()

    svcA = mgr.service_catalog_manager.register_service("Tenant_A", "Tenant A Confidential Service")

    # Tenant A access ok
    fetched = mgr.service_catalog_manager.get_service(svcA.service_id, "Tenant_A")
    assert fetched.name == "Tenant A Confidential Service"

    # Tenant B access blocked
    with pytest.raises(ServiceNotFoundException):
        mgr.service_catalog_manager.get_service(svcA.service_id, "Tenant_B")
