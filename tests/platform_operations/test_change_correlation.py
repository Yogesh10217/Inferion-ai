"""Unit tests for Change Correlation Intelligence Engine."""

from datetime import datetime, timezone
import pytest
from app.platform_operations.change_correlation import ChangeIntelligenceEngine


def test_change_correlation_with_incident():
    engine = ChangeIntelligenceEngine()
    chg = engine.record_change("t1", "DEPLOYMENT", "svc_gateway", "v2.0.1")

    now = datetime.now(timezone.utc)
    correlations = engine.correlate_incident_with_changes("t1", "inc_100", now, ["svc_gateway"])

    assert len(correlations) >= 1
    assert correlations[0].suspected_change.change_id == chg.change_id
    assert correlations[0].confidence_score >= 0.80
