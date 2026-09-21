"""Comprehensive End-to-End Test Suite for Phase 5.57 Runtime Intelligence Platform (22 Test Flows)."""

import pytest

from app.runtime_intelligence.exceptions import (
    CrossTenantRuntimeIntelligenceException,
    HighRiskRuntimeActionRequiresApprovalException,
    ImmutableRuntimeIntelligenceRecordException,
)
from app.runtime_intelligence.manager import RuntimeIntelligenceManager
from app.runtime_intelligence.models import DelegationStatus, GovernanceDecision, HealthStatus, RiskLevel


@pytest.fixture
def manager():
    return RuntimeIntelligenceManager()


# Flow 1: Signal Ingestion & Normalization
def test_flow_01_signal_ingestion_and_normalization(manager):
    obs = manager.ingest_observation(
        tenant_id="tenant_a",
        subsystem="inference_engine",
        metric_name="latency_p99",
        value=145.2,
        dimensions={"cluster": "us-east-1", "model": "gpt-4-turbo"},
    )
    assert obs.observation_id.startswith("obs-")
    assert obs.tenant_id == "tenant_a"
    assert obs.subsystem == "inference_engine"
    assert obs.value == 145.2
    assert obs.dimensions["cluster"] == "us-east-1"


# Flow 2: Multi-Dimensional Telemetry Correlation
def test_flow_02_multidimensional_telemetry_correlation(manager):
    obs1 = manager.ingest_observation("tenant_a", "database", "query_latency", 250.0)
    obs2 = manager.ingest_observation("tenant_a", "database", "cpu_utilization", 92.5)

    corr = manager.correlate_telemetry("tenant_a", "database", [obs1.observation_id, obs2.observation_id])
    assert corr.correlation_id.startswith("corr")
    assert corr.tenant_id == "tenant_a"
    assert len(corr.observation_ids) == 2
    assert 0.0 <= corr.correlation_score <= 1.0


# Flow 3: Subsystem Health Scoring
def test_flow_03_subsystem_health_scoring(manager):
    health = manager.evaluate_health(
        tenant_id="tenant_a",
        subsystem="api_gateway",
        telemetry={"error_rate": 0.02, "p95_latency": 120.0},
    )
    assert health.assessment_id.startswith("rh") or health.assessment_id.startswith("hlth")
    assert health.tenant_id == "tenant_a"
    assert health.subsystem == "api_gateway"
    assert health.overall_score >= 0.0
    assert isinstance(health.overall_health, HealthStatus)


# Flow 4: Anomaly Detection
def test_flow_04_anomaly_detection(manager):
    res = manager.detect_anomalies(
        tenant_id="tenant_a",
        subsystem="security_service",
        time_series_data=[
            {"timestamp": "2026-09-09T10:00:00Z", "value": 10.0},
            {"timestamp": "2026-09-09T10:01:00Z", "value": 10.5},
            {"timestamp": "2026-09-09T10:02:00Z", "value": 500.0},  # spike
        ],
    )
    assert "detection_id" in res
    assert res["anomalies_count"] >= 1
    assert res["highest_severity"] in ["HIGH", "CRITICAL", "MEDIUM"]


# Flow 5: Baseline Establishment & Update
def test_flow_05_baseline_establishment(manager):
    bl = manager.establish_baseline(
        tenant_id="tenant_a",
        subsystem="cache_service",
        metric_name="hit_ratio",
        sample_values=[0.95, 0.94, 0.96, 0.95, 0.97, 0.93],
    )
    assert bl.baseline_id.startswith("base-")
    assert bl.sample_count == 6
    assert 0.90 <= bl.mean <= 0.98
    assert bl.std_dev >= 0.0


# Flow 6: Configuration & Policy Drift Analysis
def test_flow_06_drift_analysis(manager):
    dr = manager.detect_drift(
        tenant_id="tenant_a",
        subsystem="auth_service",
        current_data={"max_retries": 3, "timeout_ms": 5000},
        baseline_data={"max_retries": 5, "timeout_ms": 2000},
    )
    assert dr.drift_id.startswith("drift")
    assert dr.drift_detected is True
    assert dr.drift_score > 0.0


# Flow 7: Degradation Trajectory Analysis
def test_flow_07_degradation_analysis(manager):
    deg = manager.analyze_degradation(
        tenant_id="tenant_a",
        subsystem="vector_db",
        historical_scores=[0.99, 0.95, 0.88, 0.75, 0.60],
    )
    assert deg.analysis_id.startswith("deg")
    assert deg.degradation_trend == "DEGRADED"
    assert deg.estimated_time_to_critical_seconds > 0.0


# Flow 8: Cross-Domain Causal Analysis
def test_flow_08_causal_analysis(manager):
    ca = manager.analyze_causality(
        tenant_id="tenant_a",
        symptom_id="symp-latency-spike",
        affected_subsystems=["api_gateway", "database"],
    )
    assert ca.analysis_id.startswith("caus")
    assert ca.root_cause_summary is not None
    assert 0.0 <= ca.confidence_score <= 1.0


# Flow 9: Risk Propagation Modeling
def test_flow_09_risk_propagation(manager):
    rp = manager.model_risk_propagation(
        tenant_id="tenant_a",
        source_subsystem="database",
        initial_risk_score=0.85,
    )
    assert rp.propagation_id.startswith("prop")
    assert rp.tenant_id == "tenant_a"
    assert len(rp.impacted_subsystems) >= 1


# Flow 10: System Impact Assessment
def test_flow_10_impact_assessment(manager):
    imp = manager.assess_impact(
        tenant_id="tenant_a",
        incident_id="inc-101",
        affected_components=["auth_service", "billing_service"],
    )
    assert imp.impact_id.startswith("imp")
    assert imp.severity_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


# Flow 11: Resilience Scoring
def test_flow_11_resilience_scoring(manager):
    res = manager.evaluate_resilience(
        tenant_id="tenant_a",
        subsystem="orchestrator",
    )
    assert res.assessment_id.startswith("res")
    assert 0.0 <= res.resilience_score <= 1.0


# Flow 12: Recovery Option Intelligence
def test_flow_12_recovery_intelligence(manager):
    rec = manager.plan_recovery(
        tenant_id="tenant_a",
        failed_subsystem="worker_pool",
    )
    assert rec.plan_id.startswith("rec-")
    assert len(rec.recovery_steps) >= 1


# Flow 13: Adaptive Assurance Posture Adjustment
def test_flow_13_adaptive_assurance(manager):
    aa = manager.evaluate_adaptive_assurance(
        tenant_id="tenant_a",
        target_subsystem="payment_gateway",
    )
    assert aa.posture_id.startswith("adapt-")
    assert aa.target_subsystem == "payment_gateway"


# Flow 14: Uncertainty Quantification
def test_flow_14_uncertainty_quantification(manager):
    unc = manager.quantify_uncertainty(
        tenant_id="tenant_a",
        assessment_type="HEALTH_EVALUATION",
        sample_variance=0.04,
    )
    assert unc.uncertainty_id.startswith("unc-")
    assert 0.0 <= unc.confidence_interval_lower <= unc.confidence_interval_upper <= 1.0


# Flow 15: Advisory Recommendation Generation
def test_flow_15_recommendations(manager):
    recs = manager.generate_recommendations(
        tenant_id="tenant_a",
        subsystem="cache_layer",
    )
    assert len(recs) >= 1
    for r in recs:
        assert r.auto_execute is False  # Mandatory invariant: auto_execute strictly False


# Flow 16: System Adaptation Strategy
def test_flow_16_adaptation_strategy(manager):
    strat = manager.plan_adaptation(
        tenant_id="tenant_a",
        subsystem="worker_nodes",
    )
    assert strat.strategy_id.startswith("strat-")
    assert strat.auto_execute is False  # Mandatory invariant: auto_execute strictly False


# Flow 17: Autonomous Governance Evaluation
def test_flow_17_governance_evaluation(manager):
    eval_res = manager.evaluate_governance(
        tenant_id="tenant_a",
        action="RESTART_SERVICE",
        risk_level=RiskLevel.HIGH,
    )
    assert eval_res["decision"] == GovernanceDecision.REQUIRE_APPROVAL.value
    assert eval_res["requires_human_approval"] is True


# Flow 18: Human Approval & Delegation Request
def test_flow_18_delegation_request(manager):
    del_req = manager.request_delegation(
        tenant_id="tenant_a",
        target_domain="OPERATIONS",
        action_type="SCALE_UP",
        payload={"nodes": 5},
        risk_level=RiskLevel.HIGH,
        is_approved=False,
    )
    assert del_req.delegation_id.startswith("del-")
    assert del_req.status == DelegationStatus.PENDING_APPROVAL
    assert del_req.requires_approval is True

    # Unapproved high risk action raises exception
    with pytest.raises(HighRiskRuntimeActionRequiresApprovalException):
        manager.execute_delegation(tenant_id="tenant_a", delegation_id=del_req.delegation_id)

    # Approving delegation enables execution
    approved_req = manager.approve_delegation(
        tenant_id="tenant_a", delegation_id=del_req.delegation_id, approver_id="usr_admin"
    )
    assert approved_req.status == DelegationStatus.APPROVED

    exec_res = manager.execute_delegation(tenant_id="tenant_a", delegation_id=del_req.delegation_id)
    assert exec_res.status == DelegationStatus.EXECUTED


# Flow 19: Human Review & Decision Ledger
def test_flow_19_human_review_ledger(manager):
    review = manager.record_human_review(
        tenant_id="tenant_a",
        item_id="del-101",
        reviewer_id="user_sec_admin",
        decision="APPROVED",
        justification="Operational necessity verified during incident",
    )
    assert review.review_id.startswith("rev-")
    assert review.reviewer_id == "user_sec_admin"


# Flow 20: Closed-Loop Verification
def test_flow_20_closed_loop_verification(manager):
    ver = manager.verify_action_outcome(
        tenant_id="tenant_a",
        action_id="del-101",
        expected_state={"health": "HEALTHY"},
        actual_state={"health": "HEALTHY"},
    )
    assert ver.verification_id.startswith("ver-")
    assert ver.success is True


# Flow 21: Immutable Evidence Bundle Sealing & Verification
def test_flow_21_evidence_bundle_sealing(manager):
    eb = manager.create_evidence_bundle(
        tenant_id="tenant_a",
        records=[{"event": "HEALTH_CHECK", "status": "PASS"}],
    )
    assert eb.bundle_id.startswith("ev")
    assert eb.sealed is True
    assert len(eb.integrity_hash) == 64  # SHA-256 hash length

    # Attempting to tamper with sealed evidence raises exception
    with pytest.raises(ImmutableRuntimeIntelligenceRecordException):
        manager.tamper_evidence(tenant_id="tenant_a", bundle_id=eb.bundle_id)


# Flow 22: Cross-Tenant Isolation Enforcement
def test_flow_22_cross_tenant_isolation(manager):
    eb = manager.create_evidence_bundle("tenant_a", [{"data": "secret_a"}])

    # Tenant B accessing Tenant A's evidence raises CrossTenantRuntimeIntelligenceException with no metadata leakage
    with pytest.raises(CrossTenantRuntimeIntelligenceException) as exc_info:
        manager.get_evidence("tenant_b", eb.bundle_id)

    assert "Access denied" in str(exc_info.value)


# Flow 23: Complete End-to-End Runtime Intelligence Lifecycle (Mandatory E2E)
def test_full_runtime_intelligence_lifecycle(manager):
    """Signal -> Normalization -> Context -> Health -> Anomaly -> Risk -> Recommendation -> Governance -> Approval -> Delegation -> Verification -> Evidence -> Snapshot -> Analytics"""
    tenant_id = "tenant_enterprise"
    subsystem = "llm_serving_engine"

    # 1. Ingest Signal
    obs = manager.ingest_observation(
        tenant_id=tenant_id,
        subsystem=subsystem,
        metric_name="latency_p99_ms",
        value=350.0,
        dimensions={"model": "deepseek-r1"},
    )
    assert obs.observation_id.startswith("obs")

    # 2. Evaluate Health
    health = manager.evaluate_health(
        tenant_id=tenant_id, subsystem=subsystem, raw_telemetry={"latency_p99_ms": 350.0, "error_rate": 0.002}
    )
    assert health.overall_status == HealthStatus.HEALTHY
    assert health.overall_score >= 0.85

    # 3. Detect Anomalies & Drift
    anom_result = manager.detect_anomalies(
        tenant_id=tenant_id, subsystem=subsystem, time_series_data=[{"value": 100}, {"value": 110}, {"value": 450}]
    )
    assert anom_result["anomalies_count"] == 1

    drift = manager.detect_drift(
        tenant_id=tenant_id, subsystem=subsystem, current_data={"temperature": 0.7}, baseline_data={"temperature": 0.2}
    )
    assert drift.drift_detected is True

    # 4. Analyze Causal & Risk Propagation
    causal = manager.analyze_causality(tenant_id=tenant_id, symptom_id="symp_slowdown", affected_subsystems=[subsystem])
    assert causal.confidence_score >= 0.80

    risk_prop = manager.model_risk_propagation(tenant_id=tenant_id, source_subsystem=subsystem, initial_risk_score=0.88)
    assert len(risk_prop.impacted_subsystems) > 0

    # 5. Assess Resilience
    resilience = manager.evaluate_resilience(tenant_id=tenant_id, subsystem=subsystem)
    assert resilience.resilience_score > 0.70

    # 6. Generate Recommendations (Advisory Only)
    recs = manager.generate_recommendations(tenant_id=tenant_id, subsystem=subsystem)
    assert len(recs) == 1
    assert recs[0].auto_execute is False  # Mandatory Invariant

    # 7. Governance Evaluation
    gov = manager.evaluate_governance(tenant_id=tenant_id, action="SCALE_REPLICAS", risk_level=RiskLevel.HIGH)
    assert gov["requires_human_approval"] is True

    # 8. Request & Approve Delegation
    del_req = manager.request_delegation(
        tenant_id=tenant_id,
        target_domain="CAPACITY_ORCHESTRATOR",
        action_type="SCALE_REPLICAS",
        payload={"replicas": 4},
        risk_level=RiskLevel.HIGH,
    )
    assert del_req.status == DelegationStatus.PENDING_APPROVAL

    approved_del = manager.approve_delegation(
        tenant_id=tenant_id, delegation_id=del_req.delegation_id, approver_id="admin_user"
    )
    assert approved_del.status == DelegationStatus.APPROVED

    executed_del = manager.execute_delegation(tenant_id=tenant_id, delegation_id=del_req.delegation_id)
    assert executed_del.status == DelegationStatus.EXECUTED

    # 9. Closed-Loop Verification
    verif = manager.verify_action_outcome(
        tenant_id=tenant_id,
        action_id=del_req.delegation_id,
        expected_state={"replicas": 4},
        actual_state={"replicas": 4},
    )
    assert verif.success is True

    # 10. Evidence Sealing
    ev = manager.create_evidence_bundle(tenant_id=tenant_id, records=[{"action": "SCALE_REPLICAS", "verified": True}])
    assert ev.sealed is True
    assert len(ev.integrity_hash) == 64

    # 11. Snapshot Capture & Verification
    snap = manager.capture_snapshot(tenant_id=tenant_id)
    assert snap.snapshot_id.startswith("snap_")
    assert snap.is_finalized is True
    assert snap.records_count >= 1

    verify_snap = manager.snapshot_manager.verify_snapshot(tenant_id=tenant_id, snapshot_id=snap.snapshot_id)
    assert verify_snap["is_valid"] is True

    # 12. FinOps Billing Tracking
    billing = manager.billing.get_usage_summary(tenant_id=tenant_id)
    assert billing["total_cost_usd"] >= 0.0


# Flow 24: Lifecycle State Machine Transitions & Invariant Validation
def test_flow_24_canonical_lifecycle_transitions():
    from app.runtime_intelligence.exceptions import InvalidRuntimeStateTransitionException
    from app.runtime_intelligence.runtime_lifecycle import RuntimeLifecycleManager, RuntimeLifecycleState

    lm = RuntimeLifecycleManager()
    assert lm.current_state == RuntimeLifecycleState.OBSERVED

    # Valid transitions
    lm.transition_to(RuntimeLifecycleState.ANALYZING, "Starting analysis")
    assert lm.current_state == RuntimeLifecycleState.ANALYZING

    lm.transition_to(RuntimeLifecycleState.HEALTH_ASSESSED, "Health computed")
    assert lm.current_state == RuntimeLifecycleState.HEALTH_ASSESSED

    lm.transition_to(RuntimeLifecycleState.RISK_ASSESSED, "Risk scored")
    assert lm.current_state == RuntimeLifecycleState.RISK_ASSESSED

    # Invalid transition directly to CLOSED from RISK_ASSESSED without intermediate step
    lm.transition_to(RuntimeLifecycleState.ADAPTATION_RECOMMENDED, "Proposed")
    with pytest.raises(InvalidRuntimeStateTransitionException):
        lm.transition_to(RuntimeLifecycleState.OBSERVED, "Illegal rewind")


# Flow 25: Concurrency Conflict Protection
def test_flow_25_concurrency_conflict():
    from app.runtime_intelligence.concurrency import RuntimeConcurrencyManager
    from app.runtime_intelligence.exceptions import RuntimeConcurrencyConflictException

    cm = RuntimeConcurrencyManager()
    key = cm.acquire_lock("tenant_1", "worker_pool_alpha")
    assert key == "tenant_1:worker_pool_alpha"

    # Conflicting lock attempt
    with pytest.raises(RuntimeConcurrencyConflictException):
        cm.acquire_lock("tenant_1", "worker_pool_alpha")

    # Releasing lock allows re-acquisition
    cm.release_lock("tenant_1", "worker_pool_alpha")
    cm.acquire_lock("tenant_1", "worker_pool_alpha")


# Flow 26: Idempotency Key Deduplication
def test_flow_26_idempotency_deduplication():
    from app.runtime_intelligence.idempotency import RuntimeIdempotencyManager

    im = RuntimeIdempotencyManager()
    key = im.generate_key("tenant_1", "INGEST_SIGNAL", {"payload": 123})
    assert len(key) == 64

    # First attempt succeeds
    assert im.check_and_record(key) is True
    # Second duplicate attempt is rejected
    assert im.check_and_record(key) is False


# Flow 27: Cross-Domain Provider Integration (Capacity, Reliability, Continuous, Autonomous)
def test_flow_27_cross_domain_provider_registry(manager):
    reg = manager.providers
    domains = ["capacity", "reliability", "continuous", "autonomous", "security", "operations"]

    for d in domains:
        provider = reg.get_provider(d)
        assert provider is not None
        assert provider.domain == d

        data = provider.collect_intelligence("tenant_alpha")
        assert "domain" in data
        assert data["domain"] == d
        assert "score" in data
