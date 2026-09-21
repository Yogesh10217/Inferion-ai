"""Unit tests for Intelligence Signal Fabric & Ingestion."""

import pytest

from app.intelligence_platform.exceptions import SignalValidationException
from app.intelligence_platform.signals import IntelligenceSignalManager, SignalSource, SignalType


def test_ingest_and_get_signal():
    mgr = IntelligenceSignalManager()
    sig = mgr.ingest_signal(
        "t1", SignalSource.OPERATIONS, SignalType.METRIC_THRESHOLD, "High latency observed", resource_id="svc_1"
    )
    assert sig.signal_id.startswith("sig_")

    fetched = mgr.get_signal(sig.signal_id, "t1")
    assert fetched.message == "High latency observed"


def test_signal_tenant_validation():
    mgr = IntelligenceSignalManager()
    with pytest.raises(SignalValidationException):
        mgr.ingest_signal("", SignalSource.SECURITY, SignalType.SECURITY_ALERT, "Unauthorized access")
