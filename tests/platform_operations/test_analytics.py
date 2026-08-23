"""Unit tests for Operational Analytics Engine."""

import pytest
from app.platform_operations.analytics import OperationalAnalyticsEngine


def test_operational_report_generation():
    engine = OperationalAnalyticsEngine()
    rep = engine.generate_report("t1", total_incidents=10, resolved_incidents=10, remediations_executed=8, remediations_successful=8)

    assert rep.mtta_seconds > 0
    assert rep.remediation_success_rate_pct == 100.0
    assert rep.slo_compliance_pct >= 99.0
