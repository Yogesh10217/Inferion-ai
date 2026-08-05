class KnowledgeException(Exception):
    """Base exception for the knowledge subsystem."""
    pass

class DocumentNotFoundError(KnowledgeException):
    """Raised when a requested knowledge document is not found."""
    pass

class IndexJobFailedError(KnowledgeException):
    """Raised when a document indexing job fails."""
    pass

class EmbeddingGenerationError(KnowledgeException):
    """Raised when embedding generation fails."""
    pass

class StateTransitionError(KnowledgeException):
    """Raised when an invalid document state transition is attempted."""
    pass
