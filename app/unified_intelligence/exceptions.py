"""Custom exceptions for Enterprise AI Unified Intelligence & Cross-Domain Reasoning Platform."""


class UnifiedIntelligenceException(Exception):
    """Base exception for all unified intelligence operations."""
    pass


class CrossTenantUnifiedIntelligenceException(UnifiedIntelligenceException):
    """Raised when cross-tenant access is attempted without authorization (Zero Metadata Leakage)."""
    pass


class InvalidUnifiedIntelligenceInputException(UnifiedIntelligenceException):
    """Raised when invalid input parameters are provided to unified intelligence APIs."""
    pass


class UnifiedIntelligenceProviderUnavailableException(UnifiedIntelligenceException):
    """Raised when a domain intelligence provider is unavailable or fails."""
    pass


class GovernanceUnifiedPolicyViolationException(UnifiedIntelligenceException):
    """Raised when a governance policy violation occurs."""
    pass


class UnifiedSignalNotFoundException(UnifiedIntelligenceException):
    """Raised when a unified signal is not found."""
    pass


class UnifiedInsightNotFoundException(UnifiedIntelligenceException):
    """Raised when a unified insight is not found."""
    pass


class SituationNotFoundException(UnifiedIntelligenceException):
    """Raised when an enterprise situation is not found."""
    pass


class CorrelationNotFoundException(UnifiedIntelligenceException):
    """Raised when a cross-domain correlation is not found."""
    pass


class CausalAnalysisException(UnifiedIntelligenceException):
    """Raised when causal analysis fails or invalid hypothesis transitions occur."""
    pass


class RiskPropagationException(UnifiedIntelligenceException):
    """Raised when risk propagation calculation fails."""
    pass


class ContextFusionException(UnifiedIntelligenceException):
    """Raised when context fusion fails or context window bounds are violated."""
    pass


class AssuranceCoordinationException(UnifiedIntelligenceException):
    """Raised when assurance coordination fails."""
    pass


class RecommendationNotFoundException(UnifiedIntelligenceException):
    """Raised when a recommendation is not found."""
    pass


class HighRiskUnifiedActionRequiresApprovalException(UnifiedIntelligenceException):
    """Raised when a high-risk coordinated action requires human approval before delegation."""
    pass


class ImmutableUnifiedIntelligenceRecordException(UnifiedIntelligenceException):
    """Raised when attempting to modify an immutable evidence bundle or snapshot."""
    pass


class UnifiedRemediationBlockedException(UnifiedIntelligenceException):
    """Raised when a unified remediation plan is blocked by policy or governance."""
    pass
