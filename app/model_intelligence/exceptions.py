"""Tenant-safe Exception Hierarchy for Model Intelligence Platform (Phase 5.44)."""


class ModelIntelligenceException(Exception):
    """Base exception for all Model Intelligence operations."""


class CrossTenantModelIntelligenceException(ModelIntelligenceException):
    """Raised on cross-tenant metadata or access violations.

    MUST leak ZERO metadata: no model IDs, tenant IDs, document names, vector IDs, etc.
    """

    def __init__(self, message: str = "Access denied due to tenant boundary constraints."):
        super().__init__(message)


class ModelReferenceNotFoundException(ModelIntelligenceException):
    """Raised when a model reference is not found."""


class ModelEvaluationNotFoundException(ModelIntelligenceException):
    """Raised when a model evaluation record is not found."""


class ModelPerformanceNotFoundException(ModelIntelligenceException):
    """Raised when model performance records are missing."""


class ModelDriftNotFoundException(ModelIntelligenceException):
    """Raised when model drift records are missing."""


class ModelIncidentNotFoundException(ModelIntelligenceException):
    """Raised when a model incident is not found."""


class ModelRiskNotFoundException(ModelIntelligenceException):
    """Raised when a model risk profile is missing."""


class ModelTrustNotFoundException(ModelIntelligenceException):
    """Raised when a model trust score is missing."""


class ModelGovernanceBlockedException(ModelIntelligenceException):
    """Raised when model governance policy blocks an action."""


class ModelRemediationBlockedException(ModelIntelligenceException):
    """Raised when model remediation cannot proceed."""


class HighRiskModelActionRequiresApprovalException(ModelIntelligenceException):
    """Raised when a high-risk model action requires human approval."""

    def __init__(self, action_type: str):
        super().__init__(f"High-risk model action '{action_type}' requires human approval.")


class ImmutableModelIntelligenceRecordException(ModelIntelligenceException):
    """Raised when attempting to modify a finalized or immutable record."""


class ModelAssuranceException(ModelIntelligenceException):
    """Raised when model assurance checks fail or encounter errors."""


class ModelMonitoringException(ModelIntelligenceException):
    """Raised when model monitoring encounters an error."""
