"""Unit tests for Deterministic Operational Anomaly Detector."""

import pytest
from app.platform_operations.signals import SignalManager, SignalSource, SignalType, SignalSeverity
from app.platform_operations.anomalies import AnomalyDetector, AnomalyType


def test_latency_spike_anomaly_detection():
    detector = AnomalyDetector()
    sig_mgr = SignalManager()
    s = sig_mgr.ingest_signal("t1", SignalSource.METRICS, SignalType.METRIC_THRESHOLD, "High latency", metrics={"latency_ms": 3500.0}, service_id="svc_1")

    anomalies = detector.detect_anomalies("t1", [s], latency_p95_threshold_ms=2000.0)
    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == AnomalyType.LATENCY_SPIKE
