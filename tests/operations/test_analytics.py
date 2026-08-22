"""Unit tests for OperationsAnalyticsEngine (MTTD, MTTA, MTTR, MTBF)."""

import pytest
from app.operations.analytics import OperationsAnalyticsEngine


def test_operations_analytics_reporting():
    engine = OperationsAnalyticsEngine()
    rep = engine.generate_report("t_an")

    assert rep.mttr_minutes >= 0.0
    assert rep.slo_compliance_rate > 90.0
