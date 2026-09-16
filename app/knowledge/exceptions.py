class KnowledgeException(Exception):
    """Base exception for the knowledge subsystem."""


class DocumentNotFoundError(KnowledgeException):
    """Raised when a requested knowledge document is not found."""


class IndexJobFailedError(KnowledgeException):
    """Raised when a document indexing job fails."""


class EmbeddingGenerationError(KnowledgeException):
    """Raised when embedding generation fails."""


class StateTransitionError(KnowledgeException):
    """Raised when an invalid document state transition is attempted."""
