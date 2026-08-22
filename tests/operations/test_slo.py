"""Unit tests for SLOManager measurement, rolling windows, and burn-rates."""

import pytest
from app.operations.slo import SLOManager, SLOType, SLOStatus


def test_slo_measurement_and_burn_rate():
    mgr = SLOManager()

    slo = mgr.create_slo("API Availability", 99.9, tenant_id="t_slo", slo_type=SLOType.AVAILABILITY)
    assert slo.status == SLOStatus.HEALTHY

    # Record measurement meeting target
    s1 = mgr.record_measurement(slo.slo_id, 99.95)
    assert s1.status == SLOStatus.HEALTHY
    assert s1.error_budget_remaining_percent == 100.0

    # Record measurement breaching target
    s2 = mgr.record_measurement(slo.slo_id, 99.0)
    assert s2.status == SLOStatus.BREACHED
    assert s2.burn_rate > 1.0
