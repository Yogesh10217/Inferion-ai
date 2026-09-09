"""Tenant-safe exception hierarchy for Runtime Intelligence (Phase 5.54)."""

class RuntimeIntelligenceException(Exception):
    """Base exception for all Runtime Intelligence errors."""
    def __init__(self, message: str = "Runtime Intelligence processing error"):
        super().__init__(message)


class CrossTenantRuntimeIntelligenceException(RuntimeIntelligenceException):
    """Raised when an illegal cross-tenant access attempt is detected.

    Zero metadata leakage: no tenant ID, resource ID, or existence details exposed.
    """
    def __init__(self):
        super().__init__("Access denied")


class RuntimeSignalNotFoundException(RuntimeIntelligenceException):
    def __init__(self, signal_id: str = ""):
        super().__init__("Runtime signal not found")


class RuntimeHealthNotFoundException(RuntimeIntelligenceException):
    def __init__(self, assessment_id: str = ""):
        super().__init__("Runtime health assessment not found")


class RuntimeAnomalyNotFoundException(RuntimeIntelligenceException):
    def __init__(self, anomaly_id: str = ""):
        super().__init__("Runtime anomaly record not found")


class RuntimeDriftNotFoundException(RuntimeIntelligenceException):
    def __init__(self, drift_id: str = ""):
        super().__init__("Runtime drift record not found")


class RuntimeDegradationException(RuntimeIntelligenceException):
    def __init__(self, message: str = "Runtime degradation analysis error"):
        super().__init__(message)


class RuntimeCorrelationException(RuntimeIntelligenceException):
    def __init__(self, message: str = "Runtime correlation processing error"):
        super().__init__(message)


class RuntimeResilienceException(RuntimeIntelligenceException):
    def __init__(self, message: str = "Runtime resilience assessment error"):
        super().__init__(message)


class RuntimeRiskException(RuntimeIntelligenceException):
    def __init__(self, message: str = "Runtime risk propagation error"):
        super().__init__(message)


class RuntimeRecoveryException(RuntimeIntelligenceException):
    def __init__(self, message: str = "Runtime recovery analysis error"):
        super().__init__(message)


class RuntimeRecommendationNotFoundException(RuntimeIntelligenceException):
    def __init__(self, recommendation_id: str = ""):
        super().__init__("Runtime recommendation not found")


class HighRiskRuntimeActionRequiresApprovalException(RuntimeIntelligenceException):
    def __init__(self, action_name: str = ""):
        super().__init__(f"High-risk runtime action requires explicit human approval before execution")


class ImmutableRuntimeIntelligenceRecordException(RuntimeIntelligenceException):
    def __init__(self, record_id: str = ""):
        super().__init__("Finalized SHA-256 runtime evidence record is immutable and cannot be modified")


class RuntimeGovernanceException(RuntimeIntelligenceException):
    def __init__(self, message: str = "Runtime governance evaluation error"):
        super().__init__(message)


class RuntimeProviderException(RuntimeIntelligenceException):
    def __init__(self, provider_name: str = ""):
        super().__init__(f"Runtime intelligence provider fault isolated: {provider_name}")


RuntimeIntelligenceProviderException = RuntimeProviderException


class RuntimeIdempotencyException(RuntimeIntelligenceException):
    def __init__(self, key: str = ""):
        super().__init__("Duplicate runtime intelligence operation detected")


class InvalidRuntimeStateTransitionException(RuntimeIntelligenceException):
    def __init__(self, from_state: str = "", to_state: str = ""):
        super().__init__(f"Invalid runtime state transition from '{from_state}' to '{to_state}'")


class RuntimeConcurrencyConflictException(RuntimeIntelligenceException):
    def __init__(self, resource_id: str = ""):
        super().__init__("Concurrent runtime operation conflict detected")


class RuntimeIntelligenceLimitExceededException(RuntimeIntelligenceException):
    def __init__(self, limit_name: str = ""):
        super().__init__(f"Runtime intelligence execution limit exceeded: {limit_name}")

