"""Domain exceptions for Enterprise AI Intelligence & Decision Platform."""


class IntelligenceException(Exception):
    """Base exception for intelligence platform."""


class SignalValidationException(IntelligenceException):
    """Raised when an ingested signal fails validation or tenant checks."""


class ContextAssemblyException(IntelligenceException):
    """Raised when context assembly fails authorization or bounds."""


class DecisionPolicyViolationException(IntelligenceException):
    """Raised when a proposed decision violates platform governance policies."""


class InsufficientTrustException(IntelligenceException):
    """Raised when a recommendation fails trust score requirements for autonomous execution."""


class SimulationException(IntelligenceException):
    """Raised when scenario simulation fails."""


class OptimizationException(IntelligenceException):
    """Raised when optimization constraint evaluation or candidate solving fails."""


class DecisionNotFoundException(IntelligenceException):
    """Raised when a decision is not found."""

    def __init__(self, decision_id: str):
        super().__init__(f"Decision '{decision_id}' not found.")
        self.decision_id = decision_id


class RecommendationNotFoundException(IntelligenceException):
    """Raised when a recommendation is not found."""

    def __init__(self, recommendation_id: str):
        super().__init__(f"Recommendation '{recommendation_id}' not found.")
        self.recommendation_id = recommendation_id


class RecommendationExpiredException(IntelligenceException):
    """Raised when attempting to execute an expired recommendation."""


class RecommendationStaleException(IntelligenceException):
    """Raised when attempting to execute a stale or superseded recommendation."""
