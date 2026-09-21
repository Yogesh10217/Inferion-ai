from app.tracing.trace_attributes import TraceAttributes
from app.tracing.tracer import get_tracer, get_tracer_provider


def test_tracer_provider_initialization():
    provider = get_tracer_provider()
    assert provider.resource_attributes["service.name"] == "llm-inference-engine"

    tracer = get_tracer("test_tracer")
    span = tracer.start_span("test_span")
    span.set_attribute(TraceAttributes.ORG_ID, "org_123")
    span.end()

    assert span.name == "test_span"
    assert span.attributes[TraceAttributes.ORG_ID] == "org_123"
    assert span.end_time is not None
