from app.tracing.context_propagation import ContextPropagator
from app.tracing.trace_context import SpanContext


def test_w3c_context_propagation():
    ctx = SpanContext(trace_id="4bf92f3577b34da6a3ce929d0e0e4736", span_id="00f067aa0ba902b7")
    headers = {}
    ContextPropagator.inject(headers, ctx)

    assert "traceparent" in headers
    assert headers["traceparent"] == "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

    extracted = ContextPropagator.extract(headers)
    assert extracted is not None
    assert extracted.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert extracted.span_id == "00f067aa0ba902b7"
