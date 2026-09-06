"""Tenant-safe exceptions for Decision Governance platform."""


class DecisionGovernanceException(Exception):
    """Base exception for all decision governance operations."""
    pass


class CrossTenantDecisionGovernanceException(DecisionGovernanceException):
    """Raised when cross-tenant access is attempted. Leaks ZERO metadata."""

    def __init__(self, message: str = "Access denied"):
        super().__init__("Access denied")


class DecisionNotFoundException(DecisionGovernanceException):
    """Raised when a requested decision cannot be found."""
    pass


class DecisionPlanNotFoundException(DecisionGovernanceException):
    """Raised when a requested decision plan cannot be found."""
    pass


class RecommendationNotFoundException(DecisionGovernanceException):
    """Raised when a requested recommendation cannot be found."""
    pass


class ScenarioNotFoundException(DecisionGovernanceException):
    """Raised when a requested decision scenario cannot be found."""
    pass


class DecisionEvidenceNotFoundException(DecisionGovernanceException):
    """Raised when decision evidence cannot be found."""
    pass


class DecisionExecutionBlockedException(DecisionGovernanceException):
    """Raised when decision execution is blocked by policy or governance."""
    pass


class HighRiskDecisionRequiresApprovalException(DecisionGovernanceException):
    """Raised when a high-risk decision requires human approval."""
    pass


class DecisionConflictException(DecisionGovernanceException):
    """Raised when a decision conflict is detected."""
    pass


class ImmutableDecisionRecordException(DecisionGovernanceException):
    """Raised when an attempt is made to modify a finalized/immutable decision record."""
    pass


class DecisionPlanningException(DecisionGovernanceException):
    """Raised when autonomous planning fails or encounters invalid constraints."""
    pass


class ScenarioAnalysisException(DecisionGovernanceException):
    """Raised when scenario analysis encounters invalid configuration or variables."""
    pass


class DecisionVerificationException(DecisionGovernanceException):
    """Raised when decision outcome verification fails."""
    pass
