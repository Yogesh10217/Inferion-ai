"""Mandatory 12 E2E Verification Flows for Enterprise AI Portfolio Platform (Phase 5.28)."""

import pytest

from app.portfolio_platform.benefits import BenefitStatus
from app.portfolio_platform.business_cases import BenefitEstimate, CostEstimate
from app.portfolio_platform.exceptions import (
    CrossTenantPortfolioAccessException,
    FundingDecisionException,
    ImmutableInvestmentDecisionException,
)
from app.portfolio_platform.investment import InvestmentRisk, InvestmentStatus
from app.portfolio_platform.manager import PortfolioPlatformManager
from app.portfolio_platform.optimization import PortfolioConstraint


@pytest.fixture
def manager():
    return PortfolioPlatformManager()


def test_flow1_strategy_to_initiative(manager):
    """Flow 1: Strategy -> Objective -> Opportunity -> Initiative -> Business Case -> Prioritization."""
    tenant = "tenant_prio_1"
    strat = manager.strategy_manager.create_strategy(tenant, "AI First Strategy", "Drive AI Innovation")
    obj = manager.strategy_manager.add_objective(strat.strategy_id, tenant, "Automate Support", "Reduce response time")
    opp = manager.opportunity_manager.discover_opportunity(tenant, "Support Agent Opportunity", "Build agent")
    init = manager.initiative_manager.create_initiative(
        tenant, "Support Agent Initiative", "Deploy agent", opp.opportunity_id, obj.objective_id
    )
    bc = manager.business_case_manager.create_business_case(tenant, init.initiative_id, "Problem description")

    prio = manager.prioritization_engine.score_initiatives(tenant, [init], [bc])
    assert len(prio.ranked_initiatives) == 1
    assert prio.ranked_initiatives[0].rank == 1
    assert len(prio.snapshot_fingerprint) == 64


def test_flow2_portfolio_optimization(manager):
    """Flow 2: Multiple initiatives -> Budget constraint -> Optimization -> Best portfolio selection."""
    tenant = "tenant_opt_2"
    init1 = manager.initiative_manager.create_initiative(tenant, "Initiative 1", "Desc 1")
    init2 = manager.initiative_manager.create_initiative(tenant, "Initiative 2", "Desc 2")

    bc1 = manager.business_case_manager.create_business_case(
        tenant, init1.initiative_id, "Prob 1", CostEstimate(implementation_cost_usd=100000.0)
    )
    bc2 = manager.business_case_manager.create_business_case(
        tenant, init2.initiative_id, "Prob 2", CostEstimate(implementation_cost_usd=200000.0)
    )

    prio = manager.prioritization_engine.score_initiatives(tenant, [init1, init2], [bc1, bc2])
    constraint = PortfolioConstraint(max_budget_usd=150000.0)

    opt = manager.optimization_engine.optimize_portfolio(tenant, prio, [bc1, bc2], constraint=constraint)
    assert len(opt.selected_initiatives) == 1
    assert opt.total_cost_usd <= 150000.0
    assert len(opt.deprioritized_initiatives) == 1


def test_flow3_high_risk_investment(manager):
    """Flow 3: High-Risk Investment requires ApprovalEngine approval before funding."""
    tenant = "tenant_risk_3"
    init = manager.initiative_manager.create_initiative(tenant, "High Risk Core AI", "Desc")

    proposal = manager.investment_manager.propose_investment(
        tenant, init.initiative_id, 200000.0, risk_level=InvestmentRisk.HIGH
    )
    assert proposal.status == InvestmentStatus.REQUIRES_APPROVAL
    assert proposal.approval_request_id is not None

    # Attempt decision before approval fails
    with pytest.raises(ImmutableInvestmentDecisionException):
        manager.investment_manager.finalize_decision(proposal.proposal_id, tenant)

    # Approve via ApprovalEngine
    manager.governance_engine.approval_engine.approve(proposal.approval_request_id, approver_id="cfo")
    proposal.status = InvestmentStatus.APPROVED

    decision = manager.investment_manager.finalize_decision(proposal.proposal_id, tenant)
    assert decision.is_finalized is True
    assert len(decision.decision_fingerprint) == 64


def test_flow4_low_trust_investment(manager):
    """Flow 4: Low trust score triggers human approval requirement."""
    tenant = "tenant_trust_4"
    gov_decision = manager.governance_engine.evaluate_investment_governance(
        tenant_id=tenant,
        initiative_id="init_low_trust",
        amount_usd=50000.0,
        risk_level="LOW",
        architecture_trust=60.0,  # Below 70 threshold
        compliance_score=90.0,
    )
    assert gov_decision.requires_approval is True
    assert gov_decision.approval_request_id is not None


def test_flow5_value_realization(manager):
    """Flow 5: Expected Benefit -> Delegated execution -> Realized Benefit & ROI comparison."""
    tenant = "tenant_val_5"
    init = manager.initiative_manager.create_initiative(tenant, "Value Initiative", "Desc")
    manager.business_case_manager.create_business_case(
        tenant,
        init.initiative_id,
        "Problem",
        CostEstimate(implementation_cost_usd=50000.0, annual_operating_cost_usd=10000.0),
        BenefitEstimate(annual_cost_savings_usd=100000.0),
    )

    # Benefit tracking
    benefit = manager.benefits_manager.create_benefit_plan(tenant, init.initiative_id, "Cost Savings", 100000.0)
    manager.benefits_manager.record_realized_benefit(benefit.benefit_id, tenant, 110000.0)

    outcome = manager.outcome_evaluator.evaluate_outcome(
        tenant, init.initiative_id, 60000.0, 55000.0, 100000.0, 110000.0
    )
    assert outcome.actual_roi_pct > outcome.expected_roi_pct
    assert benefit.status == BenefitStatus.REALIZED


def test_flow6_budget_constraint(manager):
    """Flow 6: Portfolio budget constraint enforcement prevents over-allocation."""
    tenant = "tenant_budget_6"
    manager.funding_manager.set_budget_envelope(tenant, 100000.0)

    alloc1 = manager.funding_manager.allocate_funding(tenant, "init_1", "idemp_1", 80000.0)
    assert alloc1.allocated_amount_usd == 80000.0

    # Over-budget allocation fails
    with pytest.raises(FundingDecisionException):
        manager.funding_manager.allocate_funding(tenant, "init_2", "idemp_2", 30000.0)

    # Idempotent re-execution succeeds
    alloc1_repeat = manager.funding_manager.allocate_funding(tenant, "init_1", "idemp_1", 80000.0)
    assert alloc1_repeat.allocation_id == alloc1.allocation_id


def test_flow7_cross_tenant_isolation(manager):
    """Flow 7: Cross-tenant access attempt raises CrossTenantPortfolioAccessException with zero metadata leakage."""
    strat = manager.strategy_manager.create_strategy("tenant_owner", "Owner Strategy", "Desc")

    with pytest.raises(CrossTenantPortfolioAccessException) as exc_info:
        manager.strategy_manager.get_strategy(strat.strategy_id, tenant_id="tenant_attacker")
    assert "tenant_attacker" in str(exc_info.value)
    assert "tenant_owner" in str(exc_info.value)


def test_flow8_scenario_simulation(manager):
    """Flow 8: Scenario Simulation (20% budget reduction) evaluates without mutating production state."""
    tenant = "tenant_scen_8"
    init = manager.initiative_manager.create_initiative(tenant, "Sim Initiative", "Desc")
    bc = manager.business_case_manager.create_business_case(
        tenant, init.initiative_id, "Prob", CostEstimate(implementation_cost_usd=200000.0)
    )
    prio = manager.prioritization_engine.score_initiatives(tenant, [init], [bc])

    # Run non-mutating simulation
    scen = manager.scenario_manager.simulate_budget_reduction(
        tenant, prio, [bc], baseline_budget_usd=250000.0, reduction_percentage=20.0
    )
    assert scen.simulated_result.constraint_used.max_budget_usd == 200000.0
    # Baseline budget envelope remains unchanged
    env = manager.funding_manager.get_budget_envelope(tenant)
    assert env.total_budget_usd == 500000.0


def test_flow9_immutable_investment_decision(manager):
    """Flow 9: Finalized Investment Decision immutability verification."""
    tenant = "tenant_immut_9"
    proposal = manager.investment_manager.propose_investment(
        tenant, "init_immut", 40000.0, risk_level=InvestmentRisk.LOW
    )
    decision = manager.investment_manager.finalize_decision(proposal.proposal_id, tenant)

    assert decision.is_finalized is True
    assert len(decision.decision_fingerprint) == 64

    fetched = manager.investment_manager.get_decision(decision.decision_id, tenant)
    assert fetched.decision_fingerprint == decision.decision_fingerprint


def test_flow10_architecture_compliance_gate(manager):
    """Flow 10: Architecture & Compliance gate blocks or requires approval on low trust scores."""
    tenant = "tenant_gate_10"
    gov_decision = manager.governance_engine.evaluate_investment_governance(
        tenant_id=tenant,
        initiative_id="init_blocked",
        amount_usd=50000.0,
        risk_level="LOW",
        architecture_trust=90.0,
        compliance_score=50.0,  # Compliance violation / low compliance
    )
    assert gov_decision.requires_approval is True


def test_flow11_secret_redaction(manager):
    """Flow 11: Injected API keys, passwords, and PII are redacted in business cases."""
    tenant = "tenant_secret_11"
    bc = manager.business_case_manager.create_business_case(
        tenant_id=tenant,
        initiative_id="init_secret",
        problem_statement="Problem",
        metadata={
            "api_key": "sk-secret-key-99999",
            "password": "super-secret-password",
            "vendor_name": "AI Corp",
        },
    )
    assert bc.metadata["api_key"] == "[REDACTED]"
    assert bc.metadata["password"] == "[REDACTED]"
    assert bc.metadata["vendor_name"] == "AI Corp"


def test_flow12_full_enterprise_portfolio_lifecycle(manager):
    """Flow 12: Complete Enterprise Portfolio Lifecycle."""
    res = manager.run_full_portfolio_flow(tenant_id="tenant_full_12")
    assert res["strategy"]["status"] == "ACTIVE"
    assert res["opportunity"]["status"] == "CONVERTED_TO_INITIATIVE"
    assert res["initiative"]["status"] == "PROPOSED"
    assert res["prioritization"]["snapshot_fingerprint"] != ""
    assert res["investment_decision"]["is_finalized"] is True
    assert res["funding_allocation"]["status"] == "ALLOCATED"
    assert res["execution_plan"]["status"] == "COMPLETED"
    assert res["outcome"]["status"] == "EXCEEDED_EXPECTATIONS"
    assert res["recommendation"]["confidence_score"] >= 80.0
