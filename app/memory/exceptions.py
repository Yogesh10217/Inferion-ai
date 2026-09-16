"""
Memory Subsystem Exception Hierarchy
"""


class MemoryError(Exception):
    """Base exception for all memory platform errors."""


class MemoryNotFoundError(MemoryError):
    """Raised when a requested memory record or context item is not found."""


class MemoryClassificationError(MemoryError):
    """Raised when memory classification fails."""


class MemoryStorageError(MemoryError):
    """Raised when underlying database or vector store operations fail."""


class MemoryQuotaExceededError(MemoryError):
    """Raised when organization memory storage quota is exceeded."""


class TenantMemoryIsolationError(MemoryError):
    """Raised when multi-tenant isolation boundaries are violated."""


class MemoryRBACPermissionDeniedError(MemoryError):
    """Raised when RBAC validation fails for memory access."""
