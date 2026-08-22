"""Tests for TracingManager and span parent-child relationships."""

import pytest
from app.observability.tracing import TracingManager, SPAN_AGENT_EXECUTE, SPAN_TOOL_EXECUTE
from app.observability.context import ObservabilityContext
from app.observability.exceptions import TraceNotFoundException


def test_tracing_manager_start_and_end_trace():
    manager = TracingManager("test_tracer")
    ctx = ObservabilityContext(execution_id="exec-trace-1")

    span_dict = manager.start_trace(name=SPAN_AGENT_EXECUTE, context=ctx)
    assert span_dict["name"] == SPAN_AGENT_EXECUTE
    assert span_dict["attributes"]["execution_id"] == "exec-trace-1"

    end_dict = manager.end_trace(trace_id=ctx.trace_id, status="OK")
    assert end_dict["status"] == "OK"

    trace_spans = manager.get_trace(ctx.trace_id)
    assert len(trace_spans) >= 1


def test_tracing_manager_spans():
    manager = TracingManager("test_spans")
    ctx = ObservabilityContext(trace_id="tr-test-2", execution_id="exec-2")

    manager.start_trace(name=SPAN_AGENT_EXECUTE, context=ctx)
    child_span = manager.start_span(name=SPAN_TOOL_EXECUTE, context=ctx)
    
    assert child_span.name == SPAN_TOOL_EXECUTE
    
    manager.end_span(child_span, status="OK")
    manager.end_trace(ctx.trace_id)

    spans = manager.get_trace("tr-test-2")
    assert len(spans) == 2


def test_trace_not_found():
    manager = TracingManager("test_not_found")
    with pytest.raises(TraceNotFoundException):
        manager.get_trace("non-existent-trace-id")
