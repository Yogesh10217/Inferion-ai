import time
import logging
from typing import Dict, List, Optional, Any
from .trace_context import SpanContext, generate_trace_id, generate_span_id
from .context_propagation import ContextPropagator
from .sampling import Sampler, AlwaysOnSampler, SamplingResult
from .exporter import ExporterRegistry, BatchSpanProcessor, ConsoleExporter

logger = logging.getLogger(__name__)


class Span:
    """Represents a single active trace segment."""

    def __init__(
        self,
        name: str,
        context: SpanContext,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        processor: Optional[BatchSpanProcessor] = None,
    ):
        self.name = name
        self.context = context
        self.parent_span_id = parent_span_id
        self.attributes: Dict[str, Any] = attributes or {}
        self.events: List[Dict[str, Any]] = []
        self.status: str = "OK"
        self.status_description: str = ""

        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self._processor = processor

    def set_attribute(self, key: str, value: Any) -> "Span":
        self.attributes[key] = value
        return self

    def set_attributes(self, attrs: Dict[str, Any]) -> "Span":
        self.attributes.update(attrs)
        return self

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> "Span":
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })
        return self

    def record_exception(self, exception: Exception) -> "Span":
        self.status = "ERROR"
        self.status_description = str(exception)
        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            },
        )
        self.set_attribute("error", True)
        self.set_attribute("error.message", str(exception))
        return self

    def end(self) -> "Span":
        if self.end_time is None:
            self.end_time = time.time()
            if self._processor:
                self._processor.on_end(self)
        return self

    def __enter__(self) -> "Span":
        self._token = ContextPropagator.set_current_context(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.record_exception(exc_val)
        self.end()
        if hasattr(self, "_token"):
            ContextPropagator.set_current_context(None)

    def to_dict(self) -> Dict[str, Any]:
        duration_ms = (
            ((self.end_time or time.time()) - self.start_time) * 1000.0
        )
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.parent_span_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": round(duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
            "baggage": self.context.baggage,
        }


class Tracer:
    def __init__(
        self,
        name: str,
        provider: "TracerProvider",
    ):
        self.name = name
        self.provider = provider

    def start_span(
        self,
        name: str,
        parent_context: Optional[SpanContext] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        parent_ctx = parent_context or ContextPropagator.get_current_context()

        trace_id = parent_ctx.trace_id if parent_ctx else generate_trace_id()
        parent_span_id = parent_ctx.span_id if parent_ctx else None

        # Sample decision
        sampling_res = self.provider.sampler.should_sample(
            parent_ctx, trace_id, name, attributes
        )
        trace_flags = "01" if sampling_res.decision else "00"

        baggage = dict(parent_ctx.baggage) if parent_ctx else {}
        if sampling_res.attributes:
            attributes = attributes or {}
            attributes.update(sampling_res.attributes)

        ctx = SpanContext(
            trace_id=trace_id,
            span_id=generate_span_id(),
            trace_flags=trace_flags,
            baggage=baggage,
        )

        span = Span(
            name=name,
            context=ctx,
            parent_span_id=parent_span_id,
            attributes=attributes,
            processor=self.provider.processor if sampling_res.decision else None,
        )
        return span


class TracerProvider:
    """Configures global tracing options, resource metadata, samplers, and processors."""

    def __init__(
        self,
        service_name: str = "llm-inference-engine",
        service_version: str = "1.0.0",
        environment: str = "production",
        sampler: Optional[Sampler] = None,
    ):
        self.resource_attributes = {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
        }
        self.sampler = sampler or AlwaysOnSampler()
        self.exporter_registry = ExporterRegistry()
        self.processor = BatchSpanProcessor(self.exporter_registry.get_active())
        self._tracers: Dict[str, Tracer] = {}

    def get_tracer(self, name: str) -> Tracer:
        if name not in self._tracers:
            self._tracers[name] = Tracer(name, self)
        return self._tracers[name]

    def set_exporter(self, exporter_name: str):
        self.exporter_registry.set_active(exporter_name)
        self.processor.exporter = self.exporter_registry.get_active()


# Global Singleton TracerProvider
_global_tracer_provider: Optional[TracerProvider] = None


def get_tracer_provider() -> TracerProvider:
    global _global_tracer_provider
    if _global_tracer_provider is None:
        _global_tracer_provider = TracerProvider()
    return _global_tracer_provider


def get_tracer(name: str = "default") -> Tracer:
    return get_tracer_provider().get_tracer(name)
