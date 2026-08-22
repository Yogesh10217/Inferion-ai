"""Unit tests for MLOpsBillingTracker."""

import pytest
from app.mlops.billing import MLOpsBillingTracker


def test_billing_hierarchy_tracking():
    tracker = MLOpsBillingTracker()

    tracker.track_cost("t_mlops", "EVALUATION", 0.05, asset_id="ast_bill_1")
    tracker.track_cost("t_mlops", "INFERENCE", 0.02, asset_id="ast_bill_1")

    total = tracker.get_total_cost(tenant_id="t_mlops")
    assert pytest.approx(total, 0.001) == 0.07
