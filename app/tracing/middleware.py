import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .tracer import get_tracer
from .context_propagation import ContextPropagator
from .trace_attributes import TraceAttributes


class TracingMiddleware(BaseHTTPMiddleware):
    """FastAPI Middleware creating root HTTP spans, extracting context, and recording request metadata."""

    def __init__(self, app, tracer_name: str = "http_middleware"):
        super().__init__(app)
        self.tracer = get_tracer(tracer_name)

    async def dispatch(self, request: Request, call_next):
        headers = dict(request.headers)
        extracted_ctx = ContextPropagator.extract(headers)

        span_name = f"HTTP {request.method} {request.url.path}"
        span = self.tracer.start_span(
            span_name,
            parent_context=extracted_ctx,
            attributes={
                TraceAttributes.HTTP_METHOD: request.method,
                TraceAttributes.HTTP_URL: str(request.url),
                TraceAttributes.HTTP_TARGET: request.url.path,
                TraceAttributes.HTTP_USER_AGENT: headers.get("user-agent", ""),
                TraceAttributes.COMPONENT: "http_server",
            },
        )

        with span:
            response = None
            try:
                response = await call_next(request)
                span.set_attribute(TraceAttributes.HTTP_STATUS_CODE, response.status_code)

                # Inject traceparent into response headers for client tracing correlation
                response.headers["traceparent"] = span.context.to_traceparent()
                return response
            except Exception as exc:
                span.record_exception(exc)
                span.set_attribute(TraceAttributes.HTTP_STATUS_CODE, 500)
                raise exc
