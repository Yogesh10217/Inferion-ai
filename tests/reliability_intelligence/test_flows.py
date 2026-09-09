"""End-to-End Test Suite for Phase 5.55 Reliability Intelligence Subsystem."""

import pytest
from typing import Dict, Any

from app.reliability_intelligence.manager import ReliabilityIntelligenceManager
from app.reliability_intelligence.exceptions import (
    ReliabilityIntelligenceException,
    CrossTenantReliabilityIntelligenceException,
    HighRiskReliabilityActionRequiresApprovalException,
    ImmutableReliabilityRecordException,
    ServiceHealthNotFoundException,
)
from app.reliability_intelligence.models import (
    ServiceHealthStatus,
    ErrorBudgetStatus,
    FailureClassification,
)


@pytest.fixture
def manager() -> ReliabilityIntelligenceManager:
    return ReliabilityIntelligenceManager()


def test_service_health_ingestion_and_evaluation(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    service_id = "svc-auth-service"
    raw_metrics = {
        "cpu_utilization": 0.45,
        "memory_utilization": 0.50,
        "latency_p99_ms": 120.0,
        "error_rate": 0.001,
    }
    
    assessment = manager.evaluate_service_health(tenant_id, service_id, raw_metrics)
    
    assert assessment.tenant_id == tenant_id
    assert assessment.service_id == service_id
    assert assessment.overall_score >= 0.0 and assessment.overall_score <= 1.0
    assert assessment.status in [ServiceHealthStatus.HEALTHY, ServiceHealthStatus.DEGRADED, ServiceHealthStatus.UNHEALTHY, ServiceHealthStatus.UNKNOWN]


def test_tenant_isolation_boundary(manager: ReliabilityIntelligenceManager):
    tenant_a = "tenant-alpha"
    tenant_b = "tenant-beta"
    service_id = "svc-payments"
    
    sh_a = manager.evaluate_service_health(tenant_a, service_id)
    assert sh_a.tenant_id == tenant_a
    
    # Repositories must enforce strict tenant isolation
    record_a = manager.health_repo.get_by_id(tenant_a, sh_a.assessment_id)
    assert record_a is not None
    
    # Accessing across tenant boundary must raise CrossTenantReliabilityIntelligenceException
    with pytest.raises(CrossTenantReliabilityIntelligenceException):
        manager.health_repo.get_by_id(tenant_b, sh_a.assessment_id)


def test_slo_and_error_budget_tracking(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    service_id = "svc-api-gateway"
    
    slo = manager.create_slo(tenant_id, service_id, indicator_type="AVAILABILITY", target_percentage=99.9)
    assert slo.tenant_id == tenant_id
    assert slo.service_id == service_id
    assert slo.target_percentage == 99.9
    
    budget = manager.evaluate_error_budget(tenant_id, slo.slo_id, total_minutes=43.2, burn_rate=1.5)
    assert budget.tenant_id == tenant_id
    assert budget.slo_id == slo.slo_id
    assert budget.remaining_budget_minutes <= budget.total_budget_minutes
    assert budget.burn_rate == 1.5


def test_failure_prediction_and_anomalies(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    service_id = "svc-db-primary"
    
    pred = manager.predict_failure(
        tenant_id=tenant_id,
        service_id=service_id,
        recent_error_rate=0.12,
        capacity_utilization=0.92,
        horizon_minutes=60
    )
    
    assert pred.tenant_id == tenant_id
    assert pred.service_id == service_id
    assert pred.probability >= 0.0 and pred.probability <= 1.0
    assert isinstance(pred.predicted_failure_type, FailureClassification)
    assert isinstance(pred.evidence, list)


def test_dependency_graph_and_propagation(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    origin = "svc-auth"
    downstream = ["svc-checkout", "svc-recommendations", "svc-notification"]
    
    manager.dependency_graph.add_dependency(origin, "svc-checkout")
    manager.dependency_graph.add_dependency("svc-checkout", "svc-recommendations")
    
    cycles = manager.dependency_graph.detect_cycles()
    assert isinstance(cycles, list)
    
    prop = manager.analyze_propagation(tenant_id, origin, downstream)
    assert prop.tenant_id == tenant_id
    assert prop.origin_service == origin
    assert len(prop.affected_nodes) >= 1
    assert prop.propagation_probability >= 0.0 and prop.propagation_probability <= 1.0


def test_blast_radius_analyzer(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    service_id = "svc-user-service"
    
    blast = manager.blast_radius_analyzer.calculate_blast_radius(tenant_id, service_id, affected_count=3)
    assert blast["tenant_id"] == tenant_id
    assert blast["origin_service"] == service_id
    assert "blast_radius_severity" in blast


def test_degradation_planning_and_approval(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    service_id = "svc-search-index"
    
    plan = manager.plan_degradation(tenant_id, service_id, strategy="GRACEFUL")
    assert plan.tenant_id == tenant_id
    assert plan.service_id == service_id
    assert len(plan.steps) > 0
    
    # High-risk action enforcement
    with pytest.raises(HighRiskReliabilityActionRequiresApprovalException):
        manager.governance_engine.enforce_approval_check(tenant_id, "PRODUCTION_FAILOVER", is_approved=False)


def test_recovery_planning_and_readiness(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    service_id = "svc-order-db"
    
    plan = manager.plan_recovery(tenant_id, service_id, strategy="FAILOVER")
    assert plan.tenant_id == tenant_id
    assert plan.service_id == service_id
    assert plan.estimated_rto_minutes > 0
    
    readiness = manager.recovery_readiness_engine.evaluate_readiness(tenant_id, service_id)
    assert readiness["tenant_id"] == tenant_id
    assert readiness["readiness_score"] >= 0.0 and readiness["readiness_score"] <= 1.0


def test_chaos_experiment_governance(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    name = "network-latency-injection"
    target = "svc-payment-gateway"
    hypothesis = "If payment gateway latency increases by 500ms, circuit breaker trips within 3 seconds"
    
    proposal = manager.propose_chaos_experiment(tenant_id, name, target, hypothesis)
    assert proposal.tenant_id == tenant_id
    assert proposal.experiment_name == name
    assert proposal.auto_execute is False, "auto_execute must be strictly False"
    assert proposal.requires_approval is True


def test_delegation_request_creation(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    action_name = "SAFE_SERVICE_RESTART"
    params = {"service_id": "svc-worker-1", "grace_period_sec": 30}
    
    delegation = manager.create_delegation(tenant_id, action_name, params)
    assert delegation["tenant_id"] == tenant_id
    assert delegation["action_name"] == action_name
    assert delegation["status"] == "SUBMITTED"
    assert delegation["delegation_id"].startswith("del_req_")


def test_verification_and_assurance(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    action_id = "act-9921"
    
    verif = manager.verification_engine.verify_outcome(tenant_id, action_id, pre_score=0.8, post_score=0.95)
    assert verif["tenant_id"] == tenant_id
    assert verif["status"] in ["VERIFIED", "FAILED", "PENDING"]
    
    ass = manager.assurance_engine.evaluate_assurance_score(tenant_id, reliability_score=0.92)
    assert ass["tenant_id"] == tenant_id
    assert ass["assurance_score"] >= 0.0 and ass["assurance_score"] <= 1.0


def test_sha256_immutable_evidence_sealing(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    assessment_id = "ass-1001"
    payload = {"service_id": "svc-core", "score": 0.98}
    
    bundle = manager.evidence_manager.seal_evidence(tenant_id, assessment_id, payload)
    assert bundle.tenant_id == tenant_id
    assert bundle.evidence_hash != ""
    assert len(bundle.evidence_hash) == 64  # SHA-256 length
    
    # Attempting to tamper evidence payload must raise ImmutableReliabilityRecordException
    with pytest.raises(ImmutableReliabilityRecordException):
        manager.evidence_manager.update_evidence(tenant_id, bundle.evidence_id, {"tampered": True})


def test_master_reliability_assessment(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    
    master_ass = manager.evaluate_reliability(tenant_id, scope="ENTERPRISE")
    assert master_ass.tenant_id == tenant_id
    assert master_ass.score.overall_score >= 0.0 and master_ass.score.overall_score <= 1.0
    assert len(master_ass.findings) >= 0


def test_analytics_and_billing(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-alpha"
    
    report = manager.analytics.generate_report(tenant_id)
    assert report["tenant_id"] == tenant_id
    assert "reliability_trend" in report
    
    usage = manager.billing.get_usage_summary(tenant_id)
    assert usage["tenant_id"] == tenant_id
    assert "total_operations" in usage


def test_full_reliability_intelligence_lifecycle(manager: ReliabilityIntelligenceManager):
    tenant_id = "tenant-enterprise"
    service_id = "svc-core-platform"
    
    # 1. Ingest metrics and evaluate health
    sh = manager.evaluate_service_health(tenant_id, service_id, {"latency_p99_ms": 350.0, "error_rate": 0.08})
    assert sh.status in [ServiceHealthStatus.DEGRADED, ServiceHealthStatus.UNHEALTHY, ServiceHealthStatus.HEALTHY]
    
    # 2. Predict failure
    pred = manager.predict_failure(tenant_id, service_id, recent_error_rate=0.08, capacity_utilization=0.91)
    assert pred.probability > 0.0
    
    # 3. Plan safe degradation
    deg_plan = manager.plan_degradation(tenant_id, service_id, strategy="GRACEFUL")
    assert deg_plan.service_id == service_id
    
    # 4. Create delegation for safe action
    delegation = manager.create_delegation(tenant_id, "ENABLE_CIRCUIT_BREAKER", {"service_id": service_id})
    assert delegation["status"] == "SUBMITTED"
    
    # 5. Seal evidence with SHA-256
    bundle = manager.evidence_manager.seal_evidence(tenant_id, sh.assessment_id, {"prediction_id": pred.prediction_id, "degradation_id": deg_plan.plan_id})
    assert len(bundle.evidence_hash) == 64
    
    # 6. Verify master report
    master = manager.evaluate_reliability(tenant_id)
    assert master.score.overall_score > 0.0
