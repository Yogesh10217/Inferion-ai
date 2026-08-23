"""Unit tests for SLO & Error Budget Tracking Manager."""

import pytest
from app.platform_operations.slo import SLOManager, SLOType, SLOStatus


def test_slo_creation_and_indicator_update():
    mgr = SLOManager()
    slo = mgr.create_slo(tenant_id="t1", service_id="svc_api", name="API Availability", slo_type=SLOType.AVAILABILITY, target_threshold=99.9)

    assert slo.status == SLOStatus.HEALTHY
    assert slo.error_budget.remaining_budget > 0

    # Breach SLO
    updated = mgr.update_slo_indicator(slo.slo_id, "t1", current_value=99.0)
    assert updated.status == SLOStatus.BREACHED
    assert updated.error_budget.consumed_percentage == 100.0
