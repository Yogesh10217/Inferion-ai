"""Mandatory 12 E2E Verification Flows for Enterprise AI Decision Intelligence Platform (Phase 5.29)."""

import pytest
from datetime import datetime, timezone

from app.decision_intelligence.manager import DecisionIntelligenceManager
from app.decision_intelligence.context import DecisionContextType, DecisionScope, DecisionPriority
from app.decision_intelligence.evidence import EvidenceReference, EvidenceStrength
from app.decision_intelligence.scenarios import ScenarioType
from app.decision_intelligence.constraints import DecisionConstraint, ConstraintType, ConstraintSeverity
from app.decision_intelligence.tradeoffs import Tradeoff, TradeoffDimension, TradeoffSeverity
from app.decision_intelligence.recommendations import RecommendationType
from app.decision_intelligence.scoring import DecisionScoreDimension
from app.decision_intelligence.exceptions import (
    CrossTenantDecisionAccessException,
    ImmutableDecisionException,
    DecisionNotFoundException,
)


@pytest.fixture
def manager():
    return DecisionIntelligenceManager()


def test_flow1_cross_domain_decision(manager):
    """Flow 1: Architecture + Data Governance + Compliance + Portfolio signals produce unified decision."""
    tenant = "tenant_flow_1"
    res = manager.run_full_decision_flow(tenant_id=tenant, title="Cross Domain Modernization")

    assert res["decision"]["is_finalized"] is True
    assert res["context"]["tenant_id"] == tenant
    assert res["evidence"]["quality_score"] >= 90.0
    assert res["recommendation"]["recommendation_type"] in (RecommendationType.PROCEED, RecommendationType.PROCEED_WITH_CONDITIONS)


def test_flow2_hard_constraint_block(manager):
    """Flow 2: Hard compliance/policy constraint blocks an otherwise high-scoring recommendation."""
    tenant = "tenant_const_2"
    ctx = manager.context_builder.assemble_context(tenant, "Blocked Decision", "Desc")

    # Add hard constraint
    manager.constraint_manager.add_constraint(
        DecisionConstraint(
            tenant_id=tenant,
            constraint_type=ConstraintType.COMPLIANCE,
            title="Regulatory Sovereignty",
            severity=ConstraintSeverity.HARD,
            threshold_value=90.0,
        )
    )

    # Observed compliance value is 50.0 (below 90 threshold)
    const_res = manager.constraint_manager.evaluate_constraints(
        tenant_id=tenant,
        context_id=ctx.context_id,
        observed_values={ConstraintType.COMPLIANCE: 50.0, ConstraintType.RISK: 20.0},
    )

    rec = manager.recommendation_engine.generate_recommendation(
        tenant_id=tenant,
        context_id=ctx.context_id,
        constraint_result=const_res,
        risk_score=20.0,
        trust_score=95.0,
    )

    assert const_res.passed_all is False
    assert rec.recommendation_type == RecommendationType.REJECT
    assert rec.requires_approval is True


def test_flow3_scenario_comparison(manager):
    """Flow 3: Baseline, optimistic, pessimistic, and cost-optimized scenarios produce reproducible outcomes."""
    tenant = "tenant_scen_3"
    ctx = manager.context_builder.assemble_context(tenant, "Scenario Decision", "Desc")

    scen_opt = manager.scenario_manager.create_scenario(tenant, ctx.context_id, "Optimistic", ScenarioType.OPTIMISTIC)
    scen_pess = manager.scenario_manager.create_scenario(tenant, ctx.context_id, "Pessimistic", ScenarioType.PESSIMISTIC)

    sim_opt = manager.scenario_manager.simulate_scenario(scen_opt.scenario_id, tenant)
    sim_pess = manager.scenario_manager.simulate_scenario(scen_pess.scenario_id, tenant)

    assert sim_opt.simulated_outcome.expected_roi_pct > sim_pess.simulated_outcome.expected_roi_pct
    assert sim_opt.simulated_outcome.risk_score < sim_pess.simulated_outcome.risk_score


def test_flow4_low_trust_high_risk(manager):
    """Flow 4: Low trust + high risk requires human approval or blocks the decision."""
    tenant = "tenant_risk_4"
    gov_dec = manager.governance_engine.evaluate_decision_governance(
        tenant_id=tenant,
        decision_id="dec_risk_high",
        risk_score=80.0,
        trust_score=50.0,
        amount_usd=200000.0,
    )
    assert gov_dec.requires_approval is True
    assert gov_dec.approval_request_id is not None


def test_flow5_immutable_decision(manager):
    """Flow 5: Finalized decision mutation is rejected with ImmutableDecisionException."""
    tenant = "tenant_immut_5"
    dec = manager.decision_manager.create_decision(tenant, "Immutable Decision")
    finalized = manager.decision_manager.finalize_decision(dec.decision_id, tenant)

    assert finalized.is_finalized is True
    assert len(finalized.decision_fingerprint) == 64

    # Mutation attempt raises ImmutableDecisionException
    with pytest.raises(ImmutableDecisionException):
        manager.decision_manager.finalize_decision(dec.decision_id, tenant)


def test_flow6_cross_tenant_isolation(manager):
    """Flow 6: Cross-tenant decision access attempt raises CrossTenantDecisionAccessException with zero metadata leakage."""
    dec = manager.decision_manager.create_decision("tenant_owner", "Owner Secret Decision")

    with pytest.raises(CrossTenantDecisionAccessException) as exc_info:
        manager.decision_manager.get_decision(dec.decision_id, tenant_id="tenant_attacker")
    assert "tenant_attacker" in str(exc_info.value)
    assert "tenant_owner" in str(exc_info.value)


def test_flow7_tradeoff_transparency(manager):
    """Flow 7: Recommendation explicitly exposes major negative trade-offs."""
    tenant = "tenant_tradeoff_7"
    tradeoff = Tradeoff(
        dimension=TradeoffDimension.COST,
        gain_description="3x performance boost",
        sacrifice_description="2x cost overhead",
        severity=TradeoffSeverity.MAJOR,
        is_negative_impact=True,
    )
    analysis = manager.tradeoff_analyzer.analyze_tradeoffs(tenant, "ctx_7", "alt_7", [tradeoff])
    assert analysis.has_major_negative_impact is True


def test_flow8_high_risk_investment(manager):
    """Flow 8: High risk investment decision requires approval before delegation."""
    tenant = "tenant_inv_8"
    gov_dec = manager.governance_engine.evaluate_decision_governance(
        tenant_id=tenant,
        decision_id="dec_inv_8",
        risk_score=75.0,
        trust_score=80.0,
        amount_usd=150000.0,
    )
    assert gov_dec.requires_approval is True


def test_flow9_outcome_learning(manager):
    """Flow 9: Observed outcome creates learning feedback without mutating historical decision records."""
    tenant = "tenant_learn_9"
    outcome = manager.outcome_manager.record_outcome(tenant, "dec_learn_9", 100000.0, 120000.0)
    record = manager.learning_manager.process_outcome_learning(tenant, outcome)

    assert record.feedback_score >= 90.0
    assert "exceeded" in record.insight.lower()


def test_flow10_secret_redaction(manager):
    """Flow 10: Evidence metadata redacts API keys, tokens, passwords, and PII."""
    tenant = "tenant_secret_10"
    ev_ref = EvidenceReference(
        source_subsystem="DATA_GOVERNANCE",
        source_entity_id="data_001",
        description="Dataset lineage evidence",
        metadata={
            "api_key": "sk-secret-key-12345",
            "password": "super-secret-password",
            "db_host": "db.internal.net",
        },
    )
    col = manager.evidence_manager.collect_evidence(tenant, "ctx_10", [ev_ref])
    ref_meta = col.references[0].metadata

    assert ref_meta["api_key"] == "[REDACTED]"
    assert ref_meta["password"] == "[REDACTED]"
    assert ref_meta["db_host"] == "db.internal.net"


def test_flow11_reproducible_snapshot(manager):
    """Flow 11: Finalized decision snapshot produces deterministic fingerprints for reproducibility."""
    tenant = "tenant_snap_11"
    dec = manager.decision_manager.create_decision(tenant, "Reproducible Decision")
    finalized = manager.decision_manager.finalize_decision(dec.decision_id, tenant, risk_score=20.0, trust_score=90.0)

    snap = manager.decision_manager.get_snapshot(dec.decision_id, tenant)
    assert snap.fingerprint == finalized.decision_fingerprint
    assert len(snap.fingerprint) == 64


def test_flow12_full_enterprise_decision_lifecycle(manager):
    """Flow 12: Complete Decision Intelligence Lifecycle."""
    flow = manager.run_full_decision_flow(tenant_id="tenant_lifecycle_12")

    assert flow["decision"]["status"] == "FINALIZED"
    assert flow["context"]["title"] == "Enterprise AI Architecture Modernization"
    assert flow["evidence"]["quality_score"] >= 90.0
    assert flow["scenario"]["status"] == "SIMULATED"
    assert flow["risk_profile"]["overall_risk_level"] == "LOW"
    assert flow["trust_score"]["trust_band"] == "HIGH_TRUST"
    assert flow["delegation"]["status"] == "COMPLETED"
    assert flow["outcome"]["status"] in ("ACHIEVED", "EXCEEDED")
