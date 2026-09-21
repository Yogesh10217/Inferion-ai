"""Unit tests for Multi-Tenancy & Strict Tenant Isolation in Intelligence Platform."""

import pytest

from app.intelligence_platform.exceptions import SignalValidationException
from app.intelligence_platform.signals import IntelligenceSignalManager, SignalSource, SignalType


def test_cross_tenant_signal_isolation():
    mgr = IntelligenceSignalManager()
    sigA = mgr.ingest_signal("tenant_A", SignalSource.OPERATIONS, SignalType.METRIC_THRESHOLD, "Signal Tenant A")

    # Tenant A access succeeds
    fetched = mgr.get_signal(sigA.signal_id, "tenant_A")
    assert fetched.message == "Signal Tenant A"

    # Tenant B access blocked
    with pytest.raises(SignalValidationException):
        mgr.get_signal(sigA.signal_id, "tenant_B")
