"""20 Mandatory E2E Integration Test Flows for Decision Governance Platform."""

import pytest
from app.decision_governance.manager import DecisionGovernanceManager
from app.decision_governance.decisions import DecisionType, DecisionPriority, DecisionStatus, DecisionOutcome
from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    DecisionNotFoundException,
    HighRiskDecisionRequiresApprovalException,
    ImmutableDecisionRecordException,
)
from app.decision_governance.signals import DecisionSignalSource, DecisionSignalType
from app.decision_governance.correlation import CorrelationType
from app.decision_governance.scenarios import ScenarioType
from app.decision_governance.simulation import SimulationInput
from app.decision_governance.optimization import OptimizationObjective
from app.decision_governance.conflicts import ConflictType, ConflictEvidence, ConflictResolution
from app.decision_governance.delegation import DecisionDelegationAction
from app.decision_governance.evidence import DecisionEvidence
from app.platform_contracts.delegation import DelegationRequest


@pytest.fixture
def manager():
    return DecisionGovernanceManager()


def test_flow_01_decision_creation_and_tenant_isolation(manager):
    """Flow 1: Decision Creation and Tenant Isolation."""
    d1 = manager.create_decision(tenant_id="tenant_a", title="Tenant A Decision", decision_type=DecisionType.OPERATIONAL)
    assert d1.decision_id is not None
    assert d1.tenant_id == "tenant_a"
    assert d1.status == DecisionStatus.DRAFT

    fetched = manager.get_decision(d1.decision_id, tenant_id="tenant_a")
    assert fetched.title == "Tenant A Decision"


def test_flow_02_cross_tenant_decision_access_blocked(manager):
    """Flow 2: Cross-Tenant Decision Access Blocked - Verify ZERO metadata leakage."""
    d1 = manager.create_decision(tenant_id="tenant_a", title="Tenant A Secret Decision")

    with pytest.raises(CrossTenantDecisionGovernanceException) as exc_info:
        manager.get_decision(d1.decision_id, tenant_id="tenant_b")

    # Exception MUST leak ZERO metadata (generic "Access denied")
    assert str(exc_info.value) == "Access denied"
    assert "tenant_a" not in str(exc_info.value)
    assert d1.decision_id not in str(exc_info.value)


def test_flow_03_cross_domain_signal_correlation(manager):
    """Flow 3: Cross-Domain Signal Correlation."""
    s1 = manager.signals.ingest_signal(
        tenant_id="tenant_a",
        source_domain=DecisionSignalSource.OPERATIONS_INTELLIGENCE,
        signal_type=DecisionSignalType.SLOWDOWN,
        title="High API Latency",
        payload={"latency_ms": 1200},
    )
    s2 = manager.signals.ingest_signal(
        tenant_id="tenant_a",
        source_domain=DecisionSignalSource.FINOPS_INTELLIGENCE,
        signal_type=DecisionSignalType.COST_SPIKE,
        title="Spend Spike",
        payload={"cost_usd": 500},
    )

    corr = manager.correlation.correlate_signals(
        tenant_id="tenant_a",
        title="Operations-FinOps Correlation",
        signals=[s1, s2],
        correlation_type=CorrelationType.INCIDENT,
    )
    assert corr.correlation_id is not None
    assert len(corr.signals) == 2
    assert len(corr.evidence) == 1


def test_flow_04_decision_risk_assessment(manager):
    """Flow 4: Decision Risk Assessment."""
    d = manager.create_decision(tenant_id="tenant_a", title="Risk Evaluation Decision")
    risk_assessment = manager.risk.assess_risk(tenant_id="tenant_a", decision_id=d.decision_id)
    assert risk_assessment.profile.overall_risk_score >= 0.0
    assert len(risk_assessment.profile.risk_factors) > 0


def test_flow_05_decision_impact_assessment(manager):
    """Flow 5: Decision Impact Assessment."""
    d = manager.create_decision(tenant_id="tenant_a", title="Impact Decision")
    impact_assessment = manager.impact.assess_impact(tenant_id="tenant_a", decision_id=d.decision_id)
    assert impact_assessment.overall_impact_score >= 0.0
    assert len(impact_assessment.impacts) >= 2


def test_flow_06_alternative_generation(manager):
    """Flow 6: Alternative Generation."""
    d = manager.create_decision(tenant_id="tenant_a", title="Alternatives Decision")
    alt1 = manager.alternatives.create_alternative(
        tenant_id="tenant_a", decision_id=d.decision_id, name="Status Quo", description="Keep current state"
    )
    alt2 = manager.alternatives.create_alternative(
        tenant_id="tenant_a", decision_id=d.decision_id, name="Automate Optimization", description="Apply auto-tuning", is_recommended=True
    )
    assessment = manager.alternatives.evaluate_alternatives(d.decision_id, tenant_id="tenant_a")
    assert len(assessment.alternatives) == 2
    assert assessment.best_alternative_id is not None


def test_flow_07_scenario_analysis(manager):
    """Flow 7: Scenario Analysis."""
    d = manager.create_decision(tenant_id="tenant_a", title="Scenario Decision")
    base_sc = manager.scenarios.create_scenario(
        tenant_id="tenant_a", decision_id=d.decision_id, name="Baseline Scenario", scenario_type=ScenarioType.BASELINE
    )
    opt_sc = manager.scenarios.create_scenario(
        tenant_id="tenant_a", decision_id=d.decision_id, name="Optimistic Scenario", scenario_type=ScenarioType.OPTIMISTIC
    )
    scenarios = manager.scenarios.list_scenarios_for_decision(d.decision_id, tenant_id="tenant_a")
    assert len(scenarios) == 2


def test_flow_08_decision_simulation(manager):
    """Flow 8: Decision Simulation."""
    d = manager.create_decision(tenant_id="tenant_a", title="Simulated Decision")
    inp = SimulationInput(decision_id=d.decision_id, iterations=100)
    sim = manager.simulation.run_simulation(tenant_id="tenant_a", decision_id=d.decision_id, name="Cost/Risk Sim", input_params=inp)
    assert sim.simulation_id is not None
    assert sim.result.reliability_impact_score > 0.90


def test_flow_09_recommendation_generation(manager):
    """Flow 9: Recommendation Generation."""
    d = manager.create_decision(tenant_id="tenant_a", title="Recommendation Decision")
    rec = manager.recommendations.create_recommendation(
        tenant_id="tenant_a",
        decision_id=d.decision_id,
        title="Scale Down Idle Instances",
        description="Reduce unutilized worker nodes",
        rationale="Saves cost with 0 SLA risk",
    )
    recs = manager.recommendations.list_recommendations_for_decision(d.decision_id, tenant_id="tenant_a")
    assert len(recs) == 1
    assert recs[0].title == "Scale Down Idle Instances"


def test_flow_10_decision_conflict_detection(manager):
    """Flow 10: Decision Conflict Detection."""
    d = manager.create_decision(tenant_id="tenant_a", title="Conflict Decision")
    policies = [{"name": "P1", "action": "DENY"}]
    recs = [{"title": "R1", "action": "ALLOW"}]
    conflicts = manager.conflicts.detect_conflicts(tenant_id="tenant_a", decision_id=d.decision_id, policies=policies, recommendations=recs)
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == ConflictType.POLICY


def test_flow_11_priority_evaluation(manager):
    """Flow 11: Priority Evaluation."""
    d = manager.create_decision(tenant_id="tenant_a", title="Priority Decision")
    assessment = manager.priorities.evaluate_priority(tenant_id="tenant_a", decision_id=d.decision_id)
    assert assessment.score.calculated_priority in [DecisionPriority.LOW, DecisionPriority.MEDIUM, DecisionPriority.HIGH, DecisionPriority.CRITICAL]


def test_flow_12_decision_optimization(manager):
    """Flow 12: Decision Optimization."""
    d = manager.create_decision(tenant_id="tenant_a", title="Optimization Decision")
    opt = manager.optimization.optimize_decision(tenant_id="tenant_a", decision_id=d.decision_id, primary_objective=OptimizationObjective.MINIMIZE_COST)
    assert opt.result.score > 0.8
    assert len(opt.result.recommendations) > 0


def test_flow_13_explainable_decision_generation(manager):
    """Flow 13: Explainable Decision Generation."""
    d = manager.create_decision(tenant_id="tenant_a", title="Explainable Decision")
    exp = manager.explainability.generate_explanation(
        tenant_id="tenant_a",
        decision_id=d.decision_id,
        why_summary="Decision chosen to minimize spend while preserving 99.99% uptime SLA",
        expected_outcome="Save $250/mo",
    )
    assert exp.why_summary != ""
    assert len(exp.why_not_alternatives) > 0
    assert len(exp.evidence) > 0
    assert len(exp.assumptions) > 0
    assert len(exp.key_risks) > 0
    assert exp.confidence.score > 0.0


def test_flow_14_high_risk_decision_requires_approval(manager):
    """Flow 14: High-Risk Decision Requires Approval."""
    d = manager.create_decision(
        tenant_id="tenant_a", title="High Risk Production Change", decision_type=DecisionType.INFRASTRUCTURE
    )
    # Perform governed evaluation
    gov_res = manager.analyze_and_governed_evaluate(d.decision_id, tenant_id="tenant_a")
    assert gov_res.requires_human_approval is True
    assert gov_res.outcome == DecisionOutcome.REQUIRE_APPROVAL

    # Attempting to delegate without approval MUST raise HighRiskDecisionRequiresApprovalException
    act = DecisionDelegationAction(target_type="SERVICE", target_id="srv-prod", action_name="MUTATE_INFRASTRUCTURE", requires_approval=True)
    with pytest.raises(HighRiskDecisionRequiresApprovalException):
        manager.delegate_decision(d.decision_id, tenant_id="tenant_a", actions=[act])

    # Approve decision
    manager.approve_decision(d.decision_id, tenant_id="tenant_a")
    plan = manager.delegate_decision(d.decision_id, tenant_id="tenant_a", actions=[act])
    assert plan.delegation_plan_id is not None


def test_flow_15_delegation_only_enforcement(manager):
    """Flow 15: Delegation-Only Enforcement - Actions generate DelegationRequest primitives."""
    d = manager.create_decision(tenant_id="tenant_a", title="Delegated Action Decision")
    manager.analyze_and_governed_evaluate(d.decision_id, tenant_id="tenant_a")
    
    act = DecisionDelegationAction(target_type="WORKFLOW", target_id="wf-123", action_name="RESTART_WORKFLOW")
    plan = manager.delegate_decision(d.decision_id, tenant_id="tenant_a", actions=[act])

    assert len(plan.delegation_requests) == 1
    req = plan.delegation_requests[0]
    assert isinstance(req, DelegationRequest)
    assert req.tenant_id == "tenant_a"
    assert req.payload.get("target_id") == "wf-123"


def test_flow_16_sensitive_data_sanitization(manager):
    """Flow 16: Sensitive Data Sanitization."""
    raw_payload = {
        "api_key": "secret-token-12345",
        "password": "super-secret-password",
        "service_name": "payment-gateway",
    }
    sig = manager.signals.ingest_signal(
        tenant_id="tenant_a",
        source_domain=DecisionSignalSource.SECURITY_INTELLIGENCE,
        signal_type=DecisionSignalType.THREAT_DETECTED,
        title="Security Threat",
        payload=raw_payload,
    )
    assert sig.sanitized_payload.get("api_key") == "[REDACTED]"
    assert sig.sanitized_payload.get("password") == "[REDACTED]"
    assert sig.sanitized_payload.get("service_name") == "payment-gateway"


def test_flow_17_immutable_decision_evidence(manager):
    """Flow 17: Immutable Decision Evidence & Record."""
    d = manager.create_decision(tenant_id="tenant_a", title="Finalized Decision")
    item = DecisionEvidence(tenant_id="tenant_a", decision_id=d.decision_id, evidence_type="TEST", title="Evidence Item")
    bundle = manager.evidence.create_evidence_bundle("tenant_a", d.decision_id, [item])
    manager.evidence.finalize_bundle(bundle.bundle_id, "tenant_a")

    # Modifying finalized bundle raises ImmutableDecisionRecordException
    with pytest.raises(ImmutableDecisionRecordException):
        manager.evidence.finalize_bundle(bundle.bundle_id, "tenant_a")

    # Verify SHA-256 integrity
    integrity = manager.evidence.verify_integrity(bundle.bundle_id, "tenant_a")
    assert integrity.is_valid is True


def test_flow_18_decision_assurance_assessment(manager):
    """Flow 18: Decision Assurance Assessment."""
    d = manager.create_decision(tenant_id="tenant_a", title="Assurance Decision")
    assessment = manager.assurance.assess_decision_assurance(tenant_id="tenant_a", decision_id=d.decision_id)
    assert assessment.assurance_score.overall_assurance_score >= 0.85
    assert assessment.assurance_score.status == "ASSURED"


def test_flow_19_learning_does_not_auto_execute(manager):
    """Flow 19: Advisory Learning Does Not Auto-Execute (`auto_execute = False`)."""
    d = manager.create_decision(tenant_id="tenant_a", title="Learning Decision")
    record = manager.learning.record_learning(tenant_id="tenant_a", decision_id=d.decision_id)
    assert len(record.recommendations) == 1
    assert record.recommendations[0].auto_execute is False  # MANDATORY INVARIANT


def test_flow_20_full_enterprise_decision_governance_lifecycle(manager):
    """Flow 20: Full Enterprise Decision Governance Lifecycle."""
    # 1. Create decision
    d = manager.create_decision(tenant_id="enterprise_tenant", title="Full Lifecycle Optimization Decision", decision_type=DecisionType.OPERATIONAL)
    assert d.status == DecisionStatus.DRAFT

    # 2. Analyze & Evaluate
    gov_res = manager.analyze_and_governed_evaluate(d.decision_id, tenant_id="enterprise_tenant")
    assert d.status in [DecisionStatus.RECOMMENDED, DecisionStatus.REQUIRES_APPROVAL]

    # 3. If requires approval, approve
    if gov_res.requires_human_approval:
        manager.approve_decision(d.decision_id, tenant_id="enterprise_tenant")

    # 4. Delegate action
    act = DecisionDelegationAction(target_type="SERVICE", target_id="service-a", action_name="RECONFIGURE")
    manager.delegate_decision(d.decision_id, tenant_id="enterprise_tenant", actions=[act])
    assert d.status == DecisionStatus.DELEGATED

    # 5. Verify & Finalize
    finalized = manager.verify_and_finalize(d.decision_id, tenant_id="enterprise_tenant")
    assert finalized.status == DecisionStatus.FINALIZED
    assert finalized.is_immutable is True

    # 6. Immutable check
    with pytest.raises(ImmutableDecisionRecordException):
        manager.decisions.update_status(d.decision_id, tenant_id="enterprise_tenant", new_status=DecisionStatus.DRAFT)
