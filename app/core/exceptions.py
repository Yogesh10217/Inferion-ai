from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, message)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(400, message)


class ProviderUnavailableError(AppException):
    def __init__(self, message: str = "Provider unavailable"):
        super().__init__(502, message)


class AppExceptionHandler:
    """Centralized exception handler for the API layer."""

    @staticmethod
    async def handle(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
