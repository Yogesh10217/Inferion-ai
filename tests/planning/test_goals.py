"""
Tests for Goal and Hierarchy Models
"""

import pytest
from app.planning.goals import Goal, Task, SubTask, Priority, Status


def test_goal_creation():
    goal = Goal(title="Build microservice", tenant_id="tenant_1")
    assert goal.title == "Build microservice"
    assert goal.tenant_id == "tenant_1"
    assert goal.status == Status.PENDING
