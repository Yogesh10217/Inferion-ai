"""
Tests for Planner Engine
"""

import pytest
from app.planning.planner import Planner


def test_create_and_optimize_plan():
    planner = Planner()
    plan = planner.create_plan("Deploy Auth Service", description="OAuth2 backend")

    assert plan.title == "Deploy Auth Service"
    assert len(plan.tasks) == 3
    assert plan.confidence_score > 0.8

    valid = planner.validate_plan(plan)
    assert valid is True

    opt_plan = planner.optimize_plan(plan)
    assert opt_plan.confidence_score >= plan.confidence_score
