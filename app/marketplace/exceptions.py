"""Domain Exceptions for Enterprise AI Marketplace."""


class MarketplaceException(Exception):
    """Base exception for Marketplace subsystem."""

    def __init__(self, message: str, code: str = "MARKETPLACE_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class MarketplaceItemNotFoundException(MarketplaceException):
    def __init__(self, item_id: str):
        super().__init__(f"Marketplace item '{item_id}' not found", code="ITEM_NOT_FOUND", status_code=404)


class PublisherNotFoundException(MarketplaceException):
    def __init__(self, publisher_id: str):
        super().__init__(f"Publisher '{publisher_id}' not found", code="PUBLISHER_NOT_FOUND", status_code=404)


class InvalidItemLifecycleTransition(MarketplaceException):
    def __init__(self, current: str, target: str):
        super().__init__(
            f"Invalid marketplace item transition from '{current}' to '{target}'",
            code="INVALID_ITEM_LIFECYCLE",
            status_code=409,
        )


class MarketplaceReviewRejectedException(MarketplaceException):
    def __init__(self, item_id: str, reason: str):
        super().__init__(
            f"Marketplace item '{item_id}' review rejected: {reason}", code="REVIEW_REJECTED", status_code=422
        )
