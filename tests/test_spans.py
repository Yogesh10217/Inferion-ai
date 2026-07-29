import pytest
from app.tracing.span_factory import SpanFactory
from app.tracing.trace_attributes import TraceAttributes


def test_span_factory():
    span = SpanFactory.create_inference_span("openai", "gpt-4")
    assert span.name == "inference.execution"
    assert span.attributes[TraceAttributes.LLM_PROVIDER] == "openai"
    assert span.attributes[TraceAttributes.LLM_MODEL] == "gpt-4"

    plugin_span = SpanFactory.create_plugin_span("my_plugin", "before_request")
    assert plugin_span.attributes[TraceAttributes.PLUGIN_ID] == "my_plugin"
