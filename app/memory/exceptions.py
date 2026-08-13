"""
Memory Subsystem Exception Hierarchy
"""


class MemoryError(Exception):
    """Base exception for all memory platform errors."""
    pass


class MemoryNotFoundError(MemoryError):
    """Raised when a requested memory record or context item is not found."""
    pass


class MemoryClassificationError(MemoryError):
    """Raised when memory classification fails."""
    pass


class MemoryStorageError(MemoryError):
    """Raised when underlying database or vector store operations fail."""
    pass


class MemoryQuotaExceededError(MemoryError):
    """Raised when organization memory storage quota is exceeded."""
    pass


class TenantMemoryIsolationError(MemoryError):
    """Raised when multi-tenant isolation boundaries are violated."""
    pass


class MemoryRBACPermissionDeniedError(MemoryError):
    """Raised when RBAC validation fails for memory access."""
    pass
