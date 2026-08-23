"""Unit tests for Signal Correlation Engine."""

import pytest
from app.platform_operations.signals import SignalManager, SignalSource, SignalType
from app.platform_operations.correlation import CorrelationEngine


def test_correlation_by_shared_id():
    sig_mgr = SignalManager()
    corr_engine = CorrelationEngine(signal_manager=sig_mgr)

    sig_mgr.ingest_signal("t1", SignalSource.METRICS, SignalType.METRIC_THRESHOLD, "High latency", correlation_id="corr_999", service_id="svc_1")
    sig_mgr.ingest_signal("t1", SignalSource.LOGS, SignalType.LOG_ERROR, "Error response", correlation_id="corr_999", service_id="svc_1")

    clusters = corr_engine.correlate_signals(tenant_id="t1")
    assert len(clusters) >= 1
    assert clusters[0].confidence_score >= 0.90
    assert len(clusters[0].signals) == 2
