"""Knowledge Platform & Organizational Intelligence Exception Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class KnowledgePlatformException(AppException):
    """Base exception for all Knowledge Platform errors."""

    def __init__(
        self,
        message: str,
        code: str = "KNOWLEDGE_PLATFORM_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class KnowledgeNotFoundException(KnowledgePlatformException):
    def __init__(self, item_id: str) -> None:
        super().__init__(message=f"Knowledge item '{item_id}' not found", code="KNOWLEDGE_NOT_FOUND", status_code=404)


class KnowledgeAccessDeniedException(KnowledgePlatformException):
    def __init__(self, item_id: str, reason: str = "Access denied by pre-retrieval authorization policy") -> None:
        super().__init__(
            message=f"Access to knowledge item '{item_id}' denied: {reason}",
            code="KNOWLEDGE_ACCESS_DENIED",
            status_code=403,
        )


class KnowledgeConflictException(KnowledgePlatformException):
    def __init__(self, conflict_id: str, reason: str) -> None:
        super().__init__(
            message=f"Knowledge conflict '{conflict_id}' unresolved: {reason}",
            code="KNOWLEDGE_CONFLICT",
            status_code=409,
        )


class ContextBuildException(KnowledgePlatformException):
    def __init__(self, reason: str) -> None:
        super().__init__(message=f"Context building failed: {reason}", code="CONTEXT_BUILD_FAILED", status_code=422)


class RetrievalException(KnowledgePlatformException):
    def __init__(self, reason: str) -> None:
        super().__init__(message=f"Knowledge retrieval failed: {reason}", code="RETRIEVAL_FAILED", status_code=500)


class KnowledgeValidationException(KnowledgePlatformException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Knowledge validation failed: {reason}", code="KNOWLEDGE_VALIDATION_FAILED", status_code=400
        )


class MemoryNotFoundException(KnowledgePlatformException):
    def __init__(self, memory_id: str) -> None:
        super().__init__(
            message=f"Organizational memory '{memory_id}' not found", code="MEMORY_NOT_FOUND", status_code=404
        )


class KnowledgeGraphException(KnowledgePlatformException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Knowledge graph operation failed: {reason}", code="KNOWLEDGE_GRAPH_ERROR", status_code=400
        )


class ProvenanceException(KnowledgePlatformException):
    def __init__(self, item_id: str, reason: str) -> None:
        super().__init__(
            message=f"Knowledge provenance error for item '{item_id}': {reason}",
            code="PROVENANCE_ERROR",
            status_code=400,
        )
