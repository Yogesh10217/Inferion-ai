"""Unit tests for Budget Enforcement actions (BLOCK, FALLBACK, THROTTLE, REQUIRE_APPROVAL)."""

from decimal import Decimal
import pytest
from app.finops.budgets import BudgetManager, BudgetAction


def test_budget_enforcement_actions():
    mgr = BudgetManager()

    # 1. BLOCK policy
    b_block = mgr.create_budget("Block Budget", Decimal("50.0"), tenant_id="t_block", enforcement_action=BudgetAction.BLOCK)
    mgr.record_usage(b_block.budget_id, Decimal("50.0"))

    dec_block = mgr.evaluate_execution("t_block", Decimal("1.0"))
    assert dec_block.permitted is False
    assert dec_block.action == BudgetAction.BLOCK

    # 2. FALLBACK_TO_CHEAPER_MODEL policy
    b_fall = mgr.create_budget("Fallback Budget", Decimal("50.0"), tenant_id="t_fall", enforcement_action=BudgetAction.FALLBACK_TO_CHEAPER_MODEL)
    mgr.record_usage(b_fall.budget_id, Decimal("50.0"))

    dec_fall = mgr.evaluate_execution("t_fall", Decimal("1.0"))
    assert dec_fall.permitted is True
    assert dec_fall.action == BudgetAction.FALLBACK_TO_CHEAPER_MODEL
    assert dec_fall.fallback_model_id == "gpt-3.5-turbo"

    # 3. THROTTLE policy
    b_throt = mgr.create_budget("Throttle Budget", Decimal("50.0"), tenant_id="t_throt", enforcement_action=BudgetAction.THROTTLE)
    mgr.record_usage(b_throt.budget_id, Decimal("50.0"))

    dec_throt = mgr.evaluate_execution("t_throt", Decimal("1.0"))
    assert dec_throt.permitted is True
    assert dec_throt.action == BudgetAction.THROTTLE
    assert dec_throt.throttle_rate_limit == 2
