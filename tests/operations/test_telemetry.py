"""Unit tests for TelemetryManager ingestion and trace/request/execution correlation."""

import pytest
from app.operations.telemetry import TelemetryManager, TelemetryType, TelemetrySeverity, TelemetryContext


def test_telemetry_recording_and_correlation():
    mgr = TelemetryManager()

    ctx = TelemetryContext(
        tenant_id="t_telemetry",
        trace_id="tr_100",
        execution_id="exec_500",
    )

    evt = mgr.record_event(
        source_service="agent_runner",
        telemetry_type=TelemetryType.LOG,
        severity=TelemetrySeverity.INFO,
        message="Agent step executed successfully",
        context=ctx,
    )

    assert evt.context.trace_id == "tr_100"

    # Query correlated events by trace_id and execution_id
    res_trace = mgr.list_events(trace_id="tr_100")
    assert len(res_trace) == 1
    assert res_trace[0].event_id == evt.event_id

    res_exec = mgr.list_events(execution_id="exec_500")
    assert len(res_exec) == 1
