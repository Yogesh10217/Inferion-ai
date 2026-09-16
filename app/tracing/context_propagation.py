import contextvars
from typing import Any, Dict, Optional

from .trace_context import SpanContext

# ContextVar holding active SpanContext across async tasks
_current_span_context: contextvars.ContextVar[Optional[SpanContext]] = contextvars.ContextVar(
    "_current_span_context", default=None
)


class ContextPropagator:
    """Propagates W3C Trace Context and baggage across HTTP, AsyncIO, and event buses."""

    TRACEPARENT_HEADER = "traceparent"
    TRACESTATE_HEADER = "tracestate"
    BAGGAGE_HEADER = "baggage"

    @staticmethod
    def get_current_context() -> Optional[SpanContext]:
        return _current_span_context.get()

    @staticmethod
    def set_current_context(ctx: Optional[SpanContext]):
        return _current_span_context.set(ctx)

    @classmethod
    def inject(cls, headers: Dict[str, str], ctx: Optional[SpanContext] = None) -> Dict[str, str]:
        """Inject current or given SpanContext into headers dictionary."""
        active_ctx = ctx or cls.get_current_context()
        if not active_ctx:
            return headers

        headers[cls.TRACEPARENT_HEADER] = active_ctx.to_traceparent()
        if active_ctx.tracestate:
            headers[cls.TRACESTATE_HEADER] = active_ctx.tracestate
        if active_ctx.baggage:
            baggage_str = ",".join(f"{k}={v}" for k, v in active_ctx.baggage.items())
            headers[cls.BAGGAGE_HEADER] = baggage_str
        return headers

    @classmethod
    def extract(cls, headers: Dict[str, str]) -> Optional[SpanContext]:
        """Extract SpanContext from headers dictionary."""
        if not headers:
            return None
        # Normalize header keys to lowercase
        norm_headers = {k.lower(): v for k, v in headers.items()}
        traceparent = norm_headers.get(cls.TRACEPARENT_HEADER)
        if not traceparent:
            return None

        baggage = {}
        baggage_raw = norm_headers.get(cls.BAGGAGE_HEADER)
        if baggage_raw:
            for item in baggage_raw.split(","):
                if "=" in item:
                    k, v = item.strip().split("=", 1)
                    baggage[k] = v

        parsed = SpanContext.from_traceparent(traceparent, baggage=baggage)
        if parsed and norm_headers.get(cls.TRACESTATE_HEADER):
            parsed.tracestate = norm_headers[cls.TRACESTATE_HEADER]
        return parsed

    @classmethod
    def propagate(cls, target_payload: Dict[str, Any], ctx: Optional[SpanContext] = None) -> Dict[str, Any]:
        """Inject trace context dictionary into event payloads or task metadata."""
        active_ctx = ctx or cls.get_current_context()
        if active_ctx:
            target_payload["_trace_context"] = {
                "traceparent": active_ctx.to_traceparent(),
                "tracestate": active_ctx.tracestate,
                "baggage": active_ctx.baggage,
            }
        return target_payload
