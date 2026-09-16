"""Tenant-safe exceptions for Knowledge Assurance platform."""


class KnowledgeAssuranceException(Exception):
    """Base exception for all knowledge assurance operations."""


class CrossTenantKnowledgeAssuranceException(KnowledgeAssuranceException):
    """Raised when cross-tenant access is attempted. Leaks ZERO metadata."""

    def __init__(self, message: str = "Access denied"):
        super().__init__("Access denied")


class KnowledgeReferenceNotFoundException(KnowledgeAssuranceException):
    """Raised when a requested knowledge reference cannot be found."""


class KnowledgeContextNotFoundException(KnowledgeAssuranceException):
    """Raised when a requested knowledge context cannot be found."""


class KnowledgeSourceNotFoundException(KnowledgeAssuranceException):
    """Raised when a requested knowledge source cannot be found."""


class KnowledgeProvenanceNotFoundException(KnowledgeAssuranceException):
    """Raised when knowledge provenance cannot be found."""


class KnowledgeConflictNotFoundException(KnowledgeAssuranceException):
    """Raised when a knowledge conflict cannot be found."""


class KnowledgeTrustNotFoundException(KnowledgeAssuranceException):
    """Raised when a knowledge trust assessment cannot be found."""


class KnowledgeEvidenceNotFoundException(KnowledgeAssuranceException):
    """Raised when knowledge evidence cannot be found."""


class KnowledgeInvestigationNotFoundException(KnowledgeAssuranceException):
    """Raised when a knowledge investigation cannot be found."""


class KnowledgeActionBlockedException(KnowledgeAssuranceException):
    """Raised when a knowledge action is blocked by governance."""


class HighRiskKnowledgeActionRequiresApprovalException(KnowledgeAssuranceException):
    """Raised when a high-risk knowledge action requires human approval."""


class ImmutableKnowledgeRecordException(KnowledgeAssuranceException):
    """Raised when an attempt is made to modify a finalized/immutable knowledge record."""


class KnowledgeContextAssemblyException(KnowledgeAssuranceException):
    """Raised when context assembly fails or encounters invalid constraints."""


class KnowledgeVerificationException(KnowledgeAssuranceException):
    """Raised when knowledge verification fails."""
