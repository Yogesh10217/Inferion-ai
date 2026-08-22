"""Unit tests for CostAnomalyDetector."""

from decimal import Decimal
import pytest
from app.finops.anomaly_detection import CostAnomalyDetector, AnomalyType, CostAnomalySeverity


def test_runaway_agent_cost_spike_detection():
    detector = CostAnomalyDetector()

    # Baseline $10 vs Observed $50 (5x threshold)
    anom = detector.detect_runaway_execution(
        tenant_id="tenant_anom",
        execution_id="run_999",
        observed_cost=Decimal("50.0"),
        baseline_cost=Decimal("10.0"),
    )

    assert anom is not None
    assert anom.anomaly_type == AnomalyType.RUNAWAY_AGENT
    assert anom.severity == CostAnomalySeverity.CRITICAL
    assert anom.recommended_action == "PAUSE_AGENT_EXECUTION"
