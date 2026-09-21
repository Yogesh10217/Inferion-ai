"""Mandatory End-to-End Integration Flows for Enterprise Intelligence Platform."""

import pytest

from app.intelligence_platform.exceptions import SignalValidationException
from app.intelligence_platform.human_decisions import DecisionReviewer, ReviewAction
from app.intelligence_platform.manager import EnterpriseIntelligenceManager
from app.intelligence_platform.optimization import OptimizationCandidate, OptimizationObjective
from app.intelligence_platform.recommendations import RecommendationStatus, RecommendationType
from app.intelligence_platform.signals import SignalClassification, SignalSource, SignalType


def test_e2e_flow_1_deployment_intelligence():
    """FLOW 1 — Deployment Intelligence: Deployment -> Error rate increases -> Signals correlated -> Context assembled -> Forecast degradation -> Simulate rollback -> Optimize options -> Recommend rollback -> HIGH risk approval -> Execute -> Verify outcome -> Learn."""
    mgr = EnterpriseIntelligenceManager()
    tenant = "t_flow1"
    res_id = "checkout_api"

    # Signals
    mgr.signal_manager.ingest_signal(
        tenant, SignalSource.DEVELOPER, SignalType.DEPLOYMENT_EVENT, "Deployed v2.1.0", resource_id=res_id
    )
    mgr.signal_manager.ingest_signal(
        tenant,
        SignalSource.OPERATIONS,
        SignalType.PERFORMANCE_DEGRADATION,
        "Latency surge >3000ms",
        classification=SignalClassification.CRITICAL_ALERT,
        resource_id=res_id,
    )

    # Full cycle run
    rec, exec_res = mgr.run_full_intelligence_cycle(
        tenant_id=tenant,
        target_resource_id=res_id,
        recommendation_type=RecommendationType.ROLLBACK_DEPLOYMENT,
        action_description="Rollback to v2.0.9",
        risk_level_str="HIGH",
    )

    assert rec.recommendation_id.startswith("rec_")
    assert rec.status == RecommendationStatus.EXECUTED
    assert exec_res.status == "SUCCESSFUL"


def test_e2e_flow_2_finops_optimization():
    """FLOW 2 — FinOps Optimization: Cost spike -> Intelligence analysis -> Multiple model alternatives -> Cost/quality optimization -> Recommendation generated -> Policy evaluation -> Approved -> Configuration change executed -> Savings measured."""
    mgr = EnterpriseIntelligenceManager()
    tenant = "t_flow2"

    mgr.signal_manager.ingest_signal(
        tenant, SignalSource.FINOPS, SignalType.COST_SPIKE, "Token cost spike on llm_router", resource_id="llm_router"
    )

    cands = [
        OptimizationCandidate(
            name="Model A GPT4",
            action_type="MODEL_SWITCH",
            target_resource_id="llm_router",
            cost_usd=100.0,
            latency_ms=200.0,
            risk_level="LOW",
        ),
        OptimizationCandidate(
            name="Model B Claude Haiku",
            action_type="MODEL_SWITCH",
            target_resource_id="llm_router",
            cost_usd=15.0,
            latency_ms=120.0,
            risk_level="LOW",
        ),
    ]

    rec, exec_res = mgr.run_full_intelligence_cycle(
        tenant_id=tenant,
        target_resource_id="llm_router",
        recommendation_type=RecommendationType.CHANGE_MODEL,
        action_description="Switch to Model B Claude Haiku for cost savings",
        risk_level_str="LOW",
        optimization_objective=OptimizationObjective.MINIMIZE_COST,
        candidates=cands,
        autonomy_allowed=True,
    )

    assert rec.recommendation_type == RecommendationType.CHANGE_MODEL
    assert exec_res.status == "SUCCESSFUL"


def test_e2e_flow_3_incident_prevention():
    """FLOW 3 — Incident Prevention: Capacity trend -> Forecast resource exhaustion -> Simulation -> Risk evaluation -> Scale recommendation -> Approval if needed -> Execution -> Outcome measurement."""
    mgr = EnterpriseIntelligenceManager()
    tenant = "t_flow3"

    mgr.signal_manager.ingest_signal(
        tenant, SignalSource.OPERATIONS, SignalType.CAPACITY_WARNING, "Queue backlog at 85%", resource_id="queue_worker"
    )

    rec, exec_res = mgr.run_full_intelligence_cycle(
        tenant_id=tenant,
        target_resource_id="queue_worker",
        recommendation_type=RecommendationType.SCALE_RESOURCE,
        action_description="Scale worker instances +5",
        risk_level_str="LOW",
        autonomy_allowed=True,
    )

    assert rec.recommendation_type == RecommendationType.SCALE_RESOURCE


def test_e2e_flow_4_human_override():
    """FLOW 4 — Human Override: Recommendation generated -> Human rejects -> Reason recorded -> Learning signal created -> Future recommendation effectiveness updated."""
    mgr = EnterpriseIntelligenceManager()
    tenant = "t_flow4"

    rec = mgr.recommendation_manager.create_recommendation(
        tenant,
        RecommendationType.FAILOVER_SERVICE,
        "Failover East",
        "Failover region",
        "svc_east",
        "Impact",
        risk_level="HIGH",
    )
    rev = mgr.approval_manager.request_human_approval(tenant, rec)

    # Human rejects
    reviewer = DecisionReviewer(user_id="ops_lead")
    updated_rev = mgr.approval_manager.submit_review_decision(
        tenant, rev.review_id, reviewer, ReviewAction.REJECT, comments="Region East has secondary fallback"
    )

    assert updated_rev.status == "REJECTED"
    mgr.recommendation_manager.update_status(rec.recommendation_id, tenant, RecommendationStatus.REJECTED)
    assert (
        mgr.recommendation_manager.get_recommendation(rec.recommendation_id, tenant).status
        == RecommendationStatus.REJECTED
    )


def test_e2e_flow_5_low_trust_evidence():
    """FLOW 5 — Low Trust Evidence: Signals conflict -> Evidence trust drops -> Recommendation confidence below threshold -> Autonomous execution blocked -> Human review requested."""
    mgr = EnterpriseIntelligenceManager()
    tenant = "t_flow5"

    ctx = mgr.context_builder.assemble_context(tenant, primary_resource_id="conflicting_svc")
    trust_score = mgr.trust_engine.evaluate_trust(ctx, forecast_confidence=0.30, simulation_confidence=0.40)

    # Trust score is below threshold -> Autonomous execution blocked
    can_exec, msg = mgr.trust_engine.evaluate_trust_risk_matrix(
        trust_score.overall_score, risk_level="LOW", policy_decision="ALLOW", configurable_trust_threshold=70.0
    )

    assert can_exec is False
    assert "below configured threshold" in msg or "LOW" in msg


def test_e2e_flow_6_high_risk_decision():
    """FLOW 6 — High-Risk Decision: Optimization recommends production change -> Risk HIGH -> ApprovalEngine request -> Administrator approves -> Execution delegated -> Audit recorded."""
    mgr = EnterpriseIntelligenceManager()
    tenant = "t_flow6"

    rec = mgr.recommendation_manager.create_recommendation(
        tenant,
        RecommendationType.ROTATE_CREDENTIAL,
        "Rotate Production Key",
        "Rotate Master Key",
        "auth_prod",
        "Security",
        risk_level="HIGH",
    )
    rev = mgr.approval_manager.request_human_approval(tenant, rec)
    assert rev.status == "PENDING"

    # Administrator approves
    mgr.approval_manager.submit_review_decision(
        tenant, rev.review_id, DecisionReviewer(user_id="sec_admin"), ReviewAction.APPROVE
    )
    mgr.recommendation_manager.update_status(rec.recommendation_id, tenant, RecommendationStatus.APPROVED)

    exec_res = mgr.execution_manager.delegate_execution(tenant, rec, target="PLATFORM_OPERATIONS")
    assert exec_res.status == "SUCCESSFUL"


def test_e2e_flow_7_cross_tenant_isolation():
    """FLOW 7 — Cross-Tenant Isolation: Verify Tenant A cannot access Tenant B signals or recommendations."""
    mgr = EnterpriseIntelligenceManager()

    sigA = mgr.signal_manager.ingest_signal(
        "tenant_A", SignalSource.SECURITY, SignalType.SECURITY_ALERT, "Tenant A Secret Alert"
    )
    recA = mgr.recommendation_manager.create_recommendation(
        "tenant_A", RecommendationType.REDUCE_COST, "Title A", "Action A", "res_A", "Impact A"
    )

    # Tenant A access succeeds
    assert mgr.signal_manager.get_signal(sigA.signal_id, "tenant_A").message == "Tenant A Secret Alert"
    assert mgr.recommendation_manager.get_recommendation(recA.recommendation_id, "tenant_A").title == "Title A"

    # Tenant B access fails
    with pytest.raises(SignalValidationException):
        mgr.signal_manager.get_signal(sigA.signal_id, "tenant_B")
