"""Tenant-safe exceptions for Knowledge Assurance platform."""


class KnowledgeAssuranceException(Exception):
    """Base exception for all knowledge assurance operations."""
    pass


class CrossTenantKnowledgeAssuranceException(KnowledgeAssuranceException):
    """Raised when cross-tenant access is attempted. Leaks ZERO metadata."""

    def __init__(self, message: str = "Access denied"):
        super().__init__("Access denied")


class KnowledgeReferenceNotFoundException(KnowledgeAssuranceException):
    """Raised when a requested knowledge reference cannot be found."""
    pass


class KnowledgeContextNotFoundException(KnowledgeAssuranceException):
    """Raised when a requested knowledge context cannot be found."""
    pass


class KnowledgeSourceNotFoundException(KnowledgeAssuranceException):
    """Raised when a requested knowledge source cannot be found."""
    pass


class KnowledgeProvenanceNotFoundException(KnowledgeAssuranceException):
    """Raised when knowledge provenance cannot be found."""
    pass


class KnowledgeConflictNotFoundException(KnowledgeAssuranceException):
    """Raised when a knowledge conflict cannot be found."""
    pass


class KnowledgeTrustNotFoundException(KnowledgeAssuranceException):
    """Raised when a knowledge trust assessment cannot be found."""
    pass


class KnowledgeEvidenceNotFoundException(KnowledgeAssuranceException):
    """Raised when knowledge evidence cannot be found."""
    pass


class KnowledgeInvestigationNotFoundException(KnowledgeAssuranceException):
    """Raised when a knowledge investigation cannot be found."""
    pass


class KnowledgeActionBlockedException(KnowledgeAssuranceException):
    """Raised when a knowledge action is blocked by governance."""
    pass


class HighRiskKnowledgeActionRequiresApprovalException(KnowledgeAssuranceException):
    """Raised when a high-risk knowledge action requires human approval."""
    pass


class ImmutableKnowledgeRecordException(KnowledgeAssuranceException):
    """Raised when an attempt is made to modify a finalized/immutable knowledge record."""
    pass


class KnowledgeContextAssemblyException(KnowledgeAssuranceException):
    """Raised when context assembly fails or encounters invalid constraints."""
    pass


class KnowledgeVerificationException(KnowledgeAssuranceException):
    """Raised when knowledge verification fails."""
    pass
