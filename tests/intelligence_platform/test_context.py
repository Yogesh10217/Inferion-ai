"""Unit tests for Intelligence Context Assembly."""

import pytest
from app.intelligence_platform.signals import IntelligenceSignalManager, SignalSource, SignalType
from app.intelligence_platform.context import ContextBuilder


def test_context_assembly():
    sig_mgr = IntelligenceSignalManager()
    sig = sig_mgr.ingest_signal("t1", SignalSource.FINOPS, SignalType.COST_SPIKE, "Cloud expenditure spike", resource_id="cluster_1")

    builder = ContextBuilder()
    ctx = builder.assemble_context("t1", primary_resource_id="cluster_1", signals=[sig])

    assert ctx.context_id.startswith("ctx_")
    assert len(ctx.signals) == 1
    assert len(ctx.evidences) >= 1
