"""
Tests for Goal and Hierarchy Models
"""

from app.planning.goals import Goal, Status


def test_goal_creation():
    goal = Goal(title="Build microservice", tenant_id="tenant_1")
    assert goal.title == "Build microservice"
    assert goal.tenant_id == "tenant_1"
    assert goal.status == Status.PENDING
