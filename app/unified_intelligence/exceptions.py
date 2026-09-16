"""Custom exceptions for Enterprise AI Unified Intelligence & Cross-Domain Reasoning Platform."""


class UnifiedIntelligenceException(Exception):
    """Base exception for all unified intelligence operations."""


class CrossTenantUnifiedIntelligenceException(UnifiedIntelligenceException):
    """Raised when cross-tenant access is attempted without authorization (Zero Metadata Leakage)."""


class InvalidUnifiedIntelligenceInputException(UnifiedIntelligenceException):
    """Raised when invalid input parameters are provided to unified intelligence APIs."""


class UnifiedIntelligenceProviderUnavailableException(UnifiedIntelligenceException):
    """Raised when a domain intelligence provider is unavailable or fails."""


class GovernanceUnifiedPolicyViolationException(UnifiedIntelligenceException):
    """Raised when a governance policy violation occurs."""


class UnifiedSignalNotFoundException(UnifiedIntelligenceException):
    """Raised when a unified signal is not found."""


class UnifiedInsightNotFoundException(UnifiedIntelligenceException):
    """Raised when a unified insight is not found."""


class SituationNotFoundException(UnifiedIntelligenceException):
    """Raised when an enterprise situation is not found."""


class CorrelationNotFoundException(UnifiedIntelligenceException):
    """Raised when a cross-domain correlation is not found."""


class CausalAnalysisException(UnifiedIntelligenceException):
    """Raised when causal analysis fails or invalid hypothesis transitions occur."""


class RiskPropagationException(UnifiedIntelligenceException):
    """Raised when risk propagation calculation fails."""


class ContextFusionException(UnifiedIntelligenceException):
    """Raised when context fusion fails or context window bounds are violated."""


class AssuranceCoordinationException(UnifiedIntelligenceException):
    """Raised when assurance coordination fails."""


class RecommendationNotFoundException(UnifiedIntelligenceException):
    """Raised when a recommendation is not found."""


class HighRiskUnifiedActionRequiresApprovalException(UnifiedIntelligenceException):
    """Raised when a high-risk coordinated action requires human approval before delegation."""


class ImmutableUnifiedIntelligenceRecordException(UnifiedIntelligenceException):
    """Raised when attempting to modify an immutable evidence bundle or snapshot."""


class UnifiedRemediationBlockedException(UnifiedIntelligenceException):
    """Raised when a unified remediation plan is blocked by policy or governance."""
