"""Mandatory End-to-End FinOps Integration Flow Verifications."""

from decimal import Decimal

from app.finops.budgets import BudgetAction
from app.finops.manager import FinOpsManager
from app.finops.optimization import OptimizationRiskLevel


def test_flow_1_model_cost_e2e_pipeline():
    mgr = FinOpsManager()

    # Model execution -> Gateway adapter -> Ledger -> Attribution -> Budget
    budget = mgr.budget_manager.create_budget("Flow 1 Budget", Decimal("10.0"), tenant_id="t_flow1")

    entry = mgr.gateway_adapter.record_inference_cost(
        tenant_id="t_flow1",
        provider="openai",
        model_id="gpt-3.5-turbo",
        prompt_tokens=2000,
        completion_tokens=1000,
    )

    assert entry.total_cost > Decimal("0.0")
    mgr.budget_manager.record_usage(budget.budget_id, entry.total_cost)

    summary = mgr.attribution_engine.attribute_tenant_costs("t_flow1")
    assert summary.direct_cost == entry.total_cost


def test_flow_2_budget_block_e2e():
    mgr = FinOpsManager()
    b = mgr.budget_manager.create_budget(
        "Block Budget", Decimal("1.0"), tenant_id="t_flow2", enforcement_action=BudgetAction.BLOCK
    )
    mgr.budget_manager.record_usage(b.budget_id, Decimal("1.0"))

    dec = mgr.budget_manager.evaluate_execution("t_flow2", Decimal("0.5"))
    assert dec.permitted is False
    assert dec.action == BudgetAction.BLOCK


def test_flow_3_cheaper_model_fallback_e2e():
    mgr = FinOpsManager()
    b = mgr.budget_manager.create_budget(
        "Fallback Budget",
        Decimal("1.0"),
        tenant_id="t_flow3",
        enforcement_action=BudgetAction.FALLBACK_TO_CHEAPER_MODEL,
    )
    mgr.budget_manager.record_usage(b.budget_id, Decimal("1.0"))

    dec = mgr.budget_manager.evaluate_execution("t_flow3", Decimal("0.5"))
    assert dec.permitted is True
    assert dec.action == BudgetAction.FALLBACK_TO_CHEAPER_MODEL
    assert dec.fallback_model_id == "gpt-3.5-turbo"

    # Execution continues using fallback model
    entry = mgr.gateway_adapter.record_inference_cost("t_flow3", "openai", dec.fallback_model_id, 1000, 500)
    assert entry.model_id == "gpt-3.5-turbo"


def test_flow_4_high_risk_optimization_approval_e2e():
    mgr = FinOpsManager()

    recs = mgr.optimization_engine.generate_recommendations("t_flow4")
    rec = recs[0]
    rec.risk_level = OptimizationRiskLevel.HIGH

    dec = mgr.governance_engine.evaluate_optimization(rec)
    assert dec.permitted is False
    assert dec.requires_approval is True

    # Simulate approval
    svg = mgr.savings_verifier.verify_savings(
        recommendation_id=rec.recommendation_id,
        baseline_cost=Decimal("100.0"),
        post_optimization_cost=Decimal("70.0"),
        tenant_id="t_flow4",
        quality_score_pre=95.0,
        quality_score_post=95.0,
    )
    assert svg.verification_status == "VERIFIED"
    assert svg.verified_savings == Decimal("30.000000")


def test_flow_5_pricing_version_immutability_e2e():
    mgr = FinOpsManager()

    # 1. Usage under Pricing v1
    e1 = mgr.gateway_adapter.record_inference_cost("t_flow5", "openai", "gpt-3.5-turbo", 1000, 1000)
    cost1 = e1.total_cost

    # 2. Update pricing catalog to v2 (Increase prices)
    mgr.pricing_manager.register_pricing(
        "openai", "gpt-3.5-turbo", input_price=Decimal("0.01"), output_price=Decimal("0.02"), version="2.0.0"
    )

    # 3. Historical ledger entry remains unchanged!
    assert e1.total_cost == cost1

    # 4. New usage uses v2 pricing
    e2 = mgr.gateway_adapter.record_inference_cost("t_flow5", "openai", "gpt-3.5-turbo", 1000, 1000)
    assert e2.total_cost > cost1
