"""Domain Exceptions for Enterprise AI Knowledge Intelligence Platform (Phase 5.35)."""


class KnowledgeIntelligenceException(Exception):
    """Base exception for all Knowledge Intelligence errors."""


class CrossTenantKnowledgeAccessException(KnowledgeIntelligenceException):
    """Raised when an attempt is made to access knowledge belonging to another tenant."""

    def __init__(self, tenant_id: str) -> None:
        super().__init__("Access denied to requested knowledge resource.")
        self.tenant_id = tenant_id


class KnowledgeNotFoundException(KnowledgeIntelligenceException):
    """Raised when a knowledge item is not found."""

    def __init__(self, item_id: str) -> None:
        super().__init__(f"Knowledge item '{item_id}' not found.")
        self.item_id = item_id


class KnowledgeSourceNotFoundException(KnowledgeIntelligenceException):
    """Raised when a knowledge source is not found."""

    def __init__(self, source_id: str) -> None:
        super().__init__(f"Knowledge source '{source_id}' not found.")
        self.source_id = source_id


class KnowledgeProvenanceException(KnowledgeIntelligenceException):
    """Raised when provenance chain validation or lookup fails."""


class KnowledgeIntegrityException(KnowledgeIntelligenceException):
    """Raised when SHA-256 integrity validation fails for a knowledge artifact."""


class KnowledgeAccessDeniedException(KnowledgeIntelligenceException):
    """Raised when access to a knowledge resource is denied by policy or authorization."""


class KnowledgeRetrievalBlockedException(KnowledgeIntelligenceException):
    """Raised when knowledge retrieval is blocked by governance rules."""


class KnowledgePolicyViolationException(KnowledgeIntelligenceException):
    """Raised when a knowledge action violates governance policies."""


class KnowledgeGraphException(KnowledgeIntelligenceException):
    """Raised when an error occurs during knowledge graph traversal or manipulation."""


class KnowledgeRelationshipNotFoundException(KnowledgeIntelligenceException):
    """Raised when a requested knowledge relationship is not found."""

    def __init__(self, relationship_id: str) -> None:
        super().__init__(f"Knowledge relationship '{relationship_id}' not found.")
        self.relationship_id = relationship_id


class ImmutableKnowledgeRecordException(KnowledgeIntelligenceException):
    """Raised when an attempt is made to mutate a finalized immutable knowledge record."""

    def __init__(self, resource_id: str) -> None:
        super().__init__(f"Knowledge record '{resource_id}' is finalized and immutable.")
        self.resource_id = resource_id


class KnowledgeRecommendationBlockedException(KnowledgeIntelligenceException):
    """Raised when a recommendation action is blocked by governance."""


class KnowledgeDelegationBlockedException(KnowledgeIntelligenceException):
    """Raised when knowledge action delegation fails or is blocked."""


class KnowledgeEvidenceValidationException(KnowledgeIntelligenceException):
    """Raised when knowledge evidence validation fails."""


class KnowledgeLearningException(KnowledgeIntelligenceException):
    """Raised when an error occurs during knowledge learning or pattern extraction."""
