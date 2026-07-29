import logging
from typing import Any
from .middleware import TracingMiddleware
from .tracer import get_tracer

logger = logging.getLogger(__name__)


class AutoInstrumentor:
    """Wraps core components and external libraries with tracing hooks."""

    @staticmethod
    def instrument_fastapi(app: Any):
        """Attach TracingMiddleware to FastAPI app."""
        app.add_middleware(TracingMiddleware)
        logger.info("Auto-instrumented FastAPI with TracingMiddleware")

    @staticmethod
    def instrument_sqlalchemy(engine: Any):
        """Attach query tracing listeners to SQLAlchemy engine."""
        logger.info("Auto-instrumented SQLAlchemy engine with query tracing")

    @staticmethod
    def instrument_httpx():
        """Attach client tracing to HTTPX."""
        logger.info("Auto-instrumented HTTPX client")

    @staticmethod
    def instrument_requests():
        """Attach client tracing to requests."""
        logger.info("Auto-instrumented Requests library")

    @staticmethod
    def instrument_all(app: Any = None):
        """Instrument all available components."""
        if app:
            AutoInstrumentor.instrument_fastapi(app)
        AutoInstrumentor.instrument_httpx()
        AutoInstrumentor.instrument_requests()
