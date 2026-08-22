"""Unit tests for DeveloperBillingTracker."""

import pytest
from app.developer_platform.billing import DeveloperBillingTracker


def test_developer_billing_tracking():
    tracker = DeveloperBillingTracker()

    rec = tracker.record_usage(
        project_id="proj_bill",
        developer_id="dev_1",
        organization_id="org_1",
        workspace_id="ws_1",
        compute_seconds=10.5,
        cost_dollars=0.15,
    )
    assert rec.total_extension_executions == 1
    assert rec.total_compute_seconds == 10.5
    assert rec.total_cost_dollars == 0.15
