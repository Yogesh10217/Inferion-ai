"""Integration Platform Exception Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class IntegrationPlatformException(AppException):
    """Base exception for all Integration Platform errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTEGRATION_PLATFORM_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class IntegrationNotFoundException(IntegrationPlatformException):
    def __init__(self, integration_id: str) -> None:
        super().__init__(
            message=f"Integration '{integration_id}' not found", code="INTEGRATION_NOT_FOUND", status_code=404
        )


class ConnectorExecutionException(IntegrationPlatformException):
    def __init__(self, connector_name: str, reason: str) -> None:
        super().__init__(
            message=f"Connector '{connector_name}' execution failed: {reason}",
            code="CONNECTOR_EXECUTION_FAILED",
            status_code=502,
        )


class WebhookSignatureException(IntegrationPlatformException):
    def __init__(self, reason: str = "Invalid webhook signature") -> None:
        super().__init__(
            message=f"Webhook signature verification failed: {reason}",
            code="WEBHOOK_SIGNATURE_INVALID",
            status_code=401,
        )


class DuplicateWebhookException(IntegrationPlatformException):
    def __init__(self, event_id: str) -> None:
        super().__init__(
            message=f"Duplicate webhook event '{event_id}' ignored", code="DUPLICATE_WEBHOOK_EVENT", status_code=409
        )


class PluginSecurityViolationException(IntegrationPlatformException):
    def __init__(self, plugin_id: str, reason: str) -> None:
        super().__init__(
            message=f"Plugin '{plugin_id}' security boundary violation: {reason}",
            code="PLUGIN_SECURITY_VIOLATION",
            status_code=403,
        )


class TransformationException(IntegrationPlatformException):
    def __init__(self, reason: str) -> None:
        super().__init__(message=f"Data transformation failed: {reason}", code="TRANSFORMATION_FAILED", status_code=422)
