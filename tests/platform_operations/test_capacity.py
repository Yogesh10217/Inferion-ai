"""Unit tests for Capacity Manager."""

import pytest
from app.platform_operations.capacity import CapacityManager, CapacityRisk


def test_capacity_assessment_and_recommendation():
    mgr = CapacityManager()

    # Normal capacity
    normal = mgr.assess_service_capacity("t1", "svc_normal", cpu_utilization_pct=40.0, queue_backlog_count=5)
    assert normal.risk == CapacityRisk.LOW
    assert normal.recommendation == "MAINTAIN"

    # Critical overloaded capacity
    overloaded = mgr.assess_service_capacity("t1", "svc_critical", cpu_utilization_pct=95.0, queue_backlog_count=600)
    assert overloaded.risk == CapacityRisk.CRITICAL
    assert overloaded.recommendation == "SCALE_UP"
