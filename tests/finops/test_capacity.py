"""Unit tests for CapacityPlanner."""

import pytest
from app.finops.capacity import CapacityPlanner


def test_capacity_planning_analysis():
    planner = CapacityPlanner()
    recs = planner.analyze_capacity("tenant_cap")

    assert len(recs) >= 2
    assert recs[0].resource_type == "WORKER_CONCURRENCY"
