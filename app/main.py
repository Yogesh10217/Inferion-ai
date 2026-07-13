import time
import uuid
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.models import router as models_router
from app.core.config import get_settings
from app.core.container import ServiceContainer
from app.core.initializer import InfrastructureInitializer
from app.core.exceptions import AppException, AppExceptionHandler, InferenceException
from app.core.logger import log_request_event, setup_logging


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs latency, status code, endpoint, and request context."""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        try:
            response = await call_next(request)
            latency_ms = (time.perf_counter() - start) * 1000
            log_request_event(
                endpoint=request.url.path,
                latency_ms=latency_ms,
                provider=request.headers.get("x-provider"),
                model=request.query_params.get("model"),
                status_code=response.status_code,
                request_id=request_id,
            )
            return response
        except AppException as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            log_request_event(
                endpoint=request.url.path,
                latency_ms=latency_ms,
                provider=request.headers.get("x-provider"),
                model=request.query_params.get("model"),
                status_code=exc.status_code,
                request_id=request_id,
                level="ERROR",
                extra={"error_code": exc.code, "error_message": exc.message},
            )
            return await AppExceptionHandler.handle(request, exc)
        except Exception as exc:  # pragma: no cover - defensive fallback
            latency_ms = (time.perf_counter() - start) * 1000
            log_request_event(
                endpoint=request.url.path,
                latency_ms=latency_ms,
                provider=request.headers.get("x-provider"),
                model=request.query_params.get("model"),
                status_code=500,
                request_id=request_id,
                level="ERROR",
                extra={"error_code": "internal_error", "error_message": str(exc)},
            )
            return JSONResponse(status_code=500, content=InferenceException().to_payload())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that handles startup initialization and graceful shutdown."""
    if hasattr(app.state, "container"):
        container = app.state.container
        initializer = InfrastructureInitializer(container)
        await initializer.initialize()
    yield
    if hasattr(app.state, "container"):
        app.state.container.logger.info("Shutting down the application and releasing resources...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    # Create service container to manage application state
    container = ServiceContainer(settings)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.state.container = container

    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.add_middleware(LoggingMiddleware)

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(models_router, prefix=settings.api_prefix)
    app.include_router(chat_router, prefix=settings.api_prefix)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"service": settings.app_name, "status": "ok"}

    return app


app = create_app()
