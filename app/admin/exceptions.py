class AdminException(Exception):
    """Base exception for all admin-related errors."""
    pass

class ResourceNotFoundException(AdminException):
    """Raised when an administrative target resource is not found."""
    pass

class InvalidOperationException(AdminException):
    """Raised when an administrative operation is invalid for the current state."""
    pass
