class AdminException(Exception):
    """Base exception for all admin-related errors."""


class ResourceNotFoundException(AdminException):
    """Raised when an administrative target resource is not found."""


class InvalidOperationException(AdminException):
    """Raised when an administrative operation is invalid for the current state."""
