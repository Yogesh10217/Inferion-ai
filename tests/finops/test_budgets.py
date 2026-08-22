"""Unit tests for BudgetManager and usage tracking."""

from decimal import Decimal
import pytest
from app.finops.budgets import BudgetManager, BudgetScope, BudgetAction, BudgetStatus


def test_budget_creation_and_status_evaluation():
    mgr = BudgetManager()

    budget = mgr.create_budget(
        name="Team Monthly Budget",
        limit_amount=Decimal("100.0"),
        tenant_id="tenant_b1",
        enforcement_action=BudgetAction.BLOCK,
    )

    assert budget.status == BudgetStatus.HEALTHY

    # Record 80% usage -> WARNING
    b1 = mgr.record_usage(budget.budget_id, Decimal("80.0"))
    assert b1.status == BudgetStatus.WARNING

    # Record total 105% usage -> EXCEEDED
    b2 = mgr.record_usage(budget.budget_id, Decimal("25.0"))
    assert b2.status == BudgetStatus.EXCEEDED
