"""Unit tests for Operational Signal Normalization & Ingestion."""

from app.platform_operations.signals import SignalManager, SignalSeverity, SignalSource, SignalType


def test_signal_ingestion_and_filtering():
    mgr = SignalManager()
    sig1 = mgr.ingest_signal(
        tenant_id="t1",
        source=SignalSource.METRICS,
        signal_type=SignalType.METRIC_THRESHOLD,
        message="High CPU utilization on node 1",
        severity=SignalSeverity.WARN,
        service_id="svc_gateway",
    )
    assert sig1.signal_id.startswith("sig_")

    signals = mgr.list_signals(tenant_id="t1", service_id="svc_gateway")
    assert len(signals) == 1
    assert signals[0].message == "High CPU utilization on node 1"
