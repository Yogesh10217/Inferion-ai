"""
Tests for Planning Decision Engine
"""

import pytest
from app.reasoning.decision_engine import PlanningDecisionEngine, StrategyOption


def test_evaluate_strategies():
    opts = [
        StrategyOption(name="Fast", description="", estimated_cost=0.001, estimated_duration_seconds=2.0, confidence_score=0.9),
        StrategyOption(name="Slow", description="", estimated_cost=0.10, estimated_duration_seconds=50.0, confidence_score=0.95),
    ]
    outcome = PlanningDecisionEngine.evaluate_strategies(opts)
    assert outcome.selected_option.name == "Fast"
