class WebhookException(Exception):
    """Base exception for all webhook and event platform errors."""


class InvalidSignatureException(WebhookException):
    """Raised when webhook signature verification fails or timestamp is expired."""


class EndpointNotFoundException(WebhookException):
    """Raised when a requested WebhookEndpoint is not found."""


class DeliveryFailedException(WebhookException):
    """Raised when webhook HTTP delivery fails after all retries."""


class EventPublishException(WebhookException):
    """Raised when publishing an event fails."""


class ReplayWindowExpiredException(WebhookException):
    """Raised when replaying an event exceeds allowed replay window."""
