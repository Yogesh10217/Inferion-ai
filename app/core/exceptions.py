from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception with a standardized API error payload."""

    def __init__(self, status_code: int, code: str, message: str, details: dict[str, Any] | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_payload(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ModelNotFoundException(AppException):
    def __init__(self, message: str = "Model not found"):
        super().__init__(404, "model_not_found", message)


class ProviderUnavailableException(AppException):
    def __init__(self, message: str = "Provider unavailable"):
        super().__init__(502, "provider_unavailable", message)


class ProviderNotFoundException(AppException):
    def __init__(self, message: str = "Provider not found"):
        super().__init__(404, "provider_not_found", message)


class RoutingException(AppException):
    def __init__(self, message: str = "Routing failed"):
        super().__init__(500, "routing_failed", message)


class InvalidRequestException(AppException):
    def __init__(self, message: str = "Invalid request"):
        super().__init__(400, "invalid_request", message)


class InferenceException(AppException):
    def __init__(self, message: str = "Inference failed"):
        super().__init__(500, "inference_failed", message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, "not_found", message)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(400, "validation_error", message)


class ProviderUnavailableError(AppException):
    def __init__(self, message: str = "Provider unavailable"):
        super().__init__(502, "provider_unavailable", message)


class AppExceptionHandler:
    """Centralized exception handler for the API layer."""

    @staticmethod
    async def handle(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_payload())
