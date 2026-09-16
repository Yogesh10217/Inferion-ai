"""
Custom exceptions for Phase 5.52 Enterprise AI Decision Intelligence Platform.
All exceptions are tenant-safe and avoid leaking sensitive metadata.
"""


class DecisionIntelligenceException(Exception):
    """Base exception for all decision intelligence operations."""


class CrossTenantDecisionIntelligenceException(DecisionIntelligenceException):
    """Raised when cross-tenant access is attempted without authorization (Zero Metadata Leakage)."""


class InvalidDecisionStateTransitionException(DecisionIntelligenceException):
    """Raised when an invalid decision lifecycle state transition is attempted."""


class DecisionNotFoundException(DecisionIntelligenceException):
    """Raised when a requested decision is not found."""


class DecisionContextNotFoundException(DecisionIntelligenceException):
    """Raised when a requested decision context is not found."""


class DecisionOptionNotFoundException(DecisionIntelligenceException):
    """Raised when a requested decision option is not found."""


class DecisionRecommendationNotFoundException(DecisionIntelligenceException):
    """Raised when a decision recommendation is not found."""


class DecisionEvidenceNotFoundException(DecisionIntelligenceException):
    """Raised when decision evidence is not found."""


class DecisionInvestigationNotFoundException(DecisionIntelligenceException):
    """Raised when a decision investigation is not found."""


class DecisionVerificationException(DecisionIntelligenceException):
    """Raised when decision verification fails."""


class DecisionAnalysisException(DecisionIntelligenceException):
    """Raised when decision analysis fails."""


class DecisionTradeoffException(DecisionIntelligenceException):
    """Raised when tradeoff evaluation fails."""


class DecisionGovernanceException(DecisionIntelligenceException):
    """Raised when decision governance policy check fails."""


class DecisionDelegationException(DecisionIntelligenceException):
    """Raised when decision delegation construction fails."""


class HighRiskDecisionRequiresApprovalException(DecisionIntelligenceException):
    """Raised when a high-risk decision action requires human approval before delegation."""


class ImmutableDecisionRecordException(DecisionIntelligenceException):
    """Raised when attempting to modify an immutable decision evidence record or snapshot."""


class DecisionRemediationBlockedException(DecisionIntelligenceException):
    """Raised when a decision remediation plan is blocked by policy or governance."""


class DecisionConstraintViolationException(DecisionIntelligenceException):
    """Raised when a decision constraint is violated."""


class DecisionScenarioException(DecisionIntelligenceException):
    """Raised when scenario evaluation fails."""


class DecisionSimulationException(DecisionIntelligenceException):
    """Raised when decision simulation fails."""


class DecisionPolicyViolationException(DecisionIntelligenceException):
    """Raised when decision policy evaluation yields a denial."""


class DecisionRiskException(DecisionIntelligenceException):
    """Raised when decision risk scoring fails."""


class DecisionApprovalRequiredException(DecisionIntelligenceException):
    """Raised when approval is required."""


class DecisionOutcomeException(DecisionIntelligenceException):
    """Raised when decision outcome verification fails."""


# Backward compatibility aliases
CrossTenantDecisionAccessException = CrossTenantDecisionIntelligenceException
DecisionContextException = DecisionContextNotFoundException
DecisionEvidenceException = DecisionEvidenceNotFoundException
DecisionRecommendationException = DecisionRecommendationNotFoundException
ImmutableDecisionException = ImmutableDecisionRecordException
