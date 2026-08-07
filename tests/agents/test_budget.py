"""
Budget Unit Tests
"""

import pytest
from app.agents.budget import AgentBudgetTracker
from app.agents.exceptions import BudgetExceededException


def test_token_budget_exceeded():
    tracker = AgentBudgetTracker(max_tokens=100)
    tracker.add_usage(50, 40)
    assert tracker.consumed_tokens == 90

    with pytest.raises(BudgetExceededException):
        tracker.add_usage(10, 10)


def test_cost_budget_exceeded():
    tracker = AgentBudgetTracker(max_cost_dollars=0.50)
    tracker.add_usage(10, 10, estimated_cost=0.30)
    assert tracker.consumed_cost_dollars == 0.30

    with pytest.raises(BudgetExceededException):
        tracker.add_usage(10, 10, estimated_cost=0.30)
