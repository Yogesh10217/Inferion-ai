"""
Custom exceptions for Phase 5.52 Enterprise AI Decision Intelligence Platform.
All exceptions are tenant-safe and avoid leaking sensitive metadata.
"""


class DecisionIntelligenceException(Exception):
    """Base exception for all decision intelligence operations."""
    pass


class CrossTenantDecisionIntelligenceException(DecisionIntelligenceException):
    """Raised when cross-tenant access is attempted without authorization (Zero Metadata Leakage)."""
    pass


class InvalidDecisionStateTransitionException(DecisionIntelligenceException):
    """Raised when an invalid decision lifecycle state transition is attempted."""
    pass


class DecisionNotFoundException(DecisionIntelligenceException):
    """Raised when a requested decision is not found."""
    pass


class DecisionContextNotFoundException(DecisionIntelligenceException):
    """Raised when a requested decision context is not found."""
    pass


class DecisionOptionNotFoundException(DecisionIntelligenceException):
    """Raised when a requested decision option is not found."""
    pass


class DecisionRecommendationNotFoundException(DecisionIntelligenceException):
    """Raised when a decision recommendation is not found."""
    pass


class DecisionEvidenceNotFoundException(DecisionIntelligenceException):
    """Raised when decision evidence is not found."""
    pass


class DecisionInvestigationNotFoundException(DecisionIntelligenceException):
    """Raised when a decision investigation is not found."""
    pass


class DecisionVerificationException(DecisionIntelligenceException):
    """Raised when decision verification fails."""
    pass


class DecisionAnalysisException(DecisionIntelligenceException):
    """Raised when decision analysis fails."""
    pass


class DecisionTradeoffException(DecisionIntelligenceException):
    """Raised when tradeoff evaluation fails."""
    pass


class DecisionGovernanceException(DecisionIntelligenceException):
    """Raised when decision governance policy check fails."""
    pass


class DecisionDelegationException(DecisionIntelligenceException):
    """Raised when decision delegation construction fails."""
    pass


class HighRiskDecisionRequiresApprovalException(DecisionIntelligenceException):
    """Raised when a high-risk decision action requires human approval before delegation."""
    pass


class ImmutableDecisionRecordException(DecisionIntelligenceException):
    """Raised when attempting to modify an immutable decision evidence record or snapshot."""
    pass


class DecisionRemediationBlockedException(DecisionIntelligenceException):
    """Raised when a decision remediation plan is blocked by policy or governance."""
    pass


class DecisionConstraintViolationException(DecisionIntelligenceException):
    """Raised when a decision constraint is violated."""
    pass


class DecisionScenarioException(DecisionIntelligenceException):
    """Raised when scenario evaluation fails."""
    pass


class DecisionSimulationException(DecisionIntelligenceException):
    """Raised when decision simulation fails."""
    pass


class DecisionPolicyViolationException(DecisionIntelligenceException):
    """Raised when decision policy evaluation yields a denial."""
    pass


class DecisionRiskException(DecisionIntelligenceException):
    """Raised when decision risk scoring fails."""
    pass


class DecisionApprovalRequiredException(DecisionIntelligenceException):
    """Raised when approval is required."""
    pass


class DecisionOutcomeException(DecisionIntelligenceException):
    """Raised when decision outcome verification fails."""
    pass


# Backward compatibility aliases
CrossTenantDecisionAccessException = CrossTenantDecisionIntelligenceException
DecisionContextException = DecisionContextNotFoundException
DecisionEvidenceException = DecisionEvidenceNotFoundException
DecisionRecommendationException = DecisionRecommendationNotFoundException
ImmutableDecisionException = ImmutableDecisionRecordException
