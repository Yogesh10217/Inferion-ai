from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.logger import log_request_event
from app.core.exceptions import AppException


class ObservationMiddleware(BaseHTTPMiddleware):
    """Middleware responsible for generating request IDs, measuring latency, and logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate Request ID
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Track latency
        start_time = time.perf_counter()

        # Initialize provider and model in request state
        request.state.provider = None
        request.state.model = None

        try:
            response = await call_next(request)
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Get metrics service if available
            metrics_service = None
            if hasattr(request.app.state, "container"):
                metrics_service = request.app.state.container.metrics_service

            is_error = response.status_code >= 400

            if metrics_service:
                metrics_service.record_request(latency_ms=latency_ms, is_error=is_error)

            client_ip = request.client.host if request.client else None
            provider = getattr(request.state, "provider", None)
            model = getattr(request.state, "model", None)

            # Log request/response event
            log_request_event(
                method=request.method,
                endpoint=request.url.path,
                latency_ms=latency_ms,
                provider=provider,
                model=model,
                status_code=response.status_code,
                client_ip=client_ip,
                request_id=request_id,
            )

            # Add X-Request-ID response header
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000
            client_ip = request.client.host if request.client else None

            status_code = 500
            error_code = "internal_error"
            error_message = str(exc)

            if isinstance(exc, AppException):
                status_code = exc.status_code
                error_code = exc.code
                error_message = exc.message

            log_request_event(
                method=request.method,
                endpoint=request.url.path,
                latency_ms=latency_ms,
                provider=getattr(request.state, "provider", None),
                model=getattr(request.state, "model", None),
                status_code=status_code,
                client_ip=client_ip,
                request_id=request_id,
                level="ERROR",
                extra={"error_code": error_code, "error_message": error_message},
            )

            metrics_service = None
            if hasattr(request.app.state, "container"):
                metrics_service = request.app.state.container.metrics_service
            if metrics_service:
                metrics_service.record_request(latency_ms=latency_ms, is_error=True)

            payload = {
                "error": {
                    "code": error_code,
                    "message": "An unexpected error occurred" if status_code == 500 else error_message,
                    "details": {}
                }
            }
            resp = JSONResponse(status_code=status_code, content=payload)
            resp.headers["X-Request-ID"] = request_id
            return resp
