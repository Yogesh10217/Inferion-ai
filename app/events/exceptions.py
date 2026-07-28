class WebhookException(Exception):
    """Base exception for all webhook and event platform errors."""
    pass


class InvalidSignatureException(WebhookException):
    """Raised when webhook signature verification fails or timestamp is expired."""
    pass


class EndpointNotFoundException(WebhookException):
    """Raised when a requested WebhookEndpoint is not found."""
    pass


class DeliveryFailedException(WebhookException):
    """Raised when webhook HTTP delivery fails after all retries."""
    pass


class EventPublishException(WebhookException):
    """Raised when publishing an event fails."""
    pass


class ReplayWindowExpiredException(WebhookException):
    """Raised when replaying an event exceeds allowed replay window."""
    pass
