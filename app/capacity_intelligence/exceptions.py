"""Tenant-safe exception hierarchy for Capacity Intelligence (Phase 5.56)."""


class CapacityIntelligenceException(Exception):
    """Base exception for all Capacity Intelligence errors."""

    def __init__(self, message: str = "Capacity Intelligence processing error"):
        super().__init__(message)


class CrossTenantCapacityIntelligenceException(CapacityIntelligenceException):
    """Raised when an illegal cross-tenant access attempt is detected.

    Zero metadata leakage: no tenant ID, resource ID, or existence details exposed.
    """

    def __init__(self):
        super().__init__("Access denied")


class CapacityAssessmentNotFoundException(CapacityIntelligenceException):
    def __init__(self, assessment_id: str = ""):
        super().__init__("Capacity assessment not found")


class CapacityForecastNotFoundException(CapacityIntelligenceException):
    def __init__(self, forecast_id: str = ""):
        super().__init__("Capacity forecast not found")


class ResourceProfileNotFoundException(CapacityIntelligenceException):
    def __init__(self, profile_id: str = ""):
        super().__init__("Resource profile not found")


class WorkloadNotFoundException(CapacityIntelligenceException):
    def __init__(self, workload_id: str = ""):
        super().__init__("Workload profile not found")


class PerformanceAssessmentNotFoundException(CapacityIntelligenceException):
    def __init__(self, assessment_id: str = ""):
        super().__init__("Performance assessment not found")


class BottleneckNotFoundException(CapacityIntelligenceException):
    def __init__(self, bottleneck_id: str = ""):
        super().__init__("Bottleneck record not found")


class SaturationPredictionException(CapacityIntelligenceException):
    def __init__(self, message: str = "Saturation prediction error"):
        super().__init__(message)


class OptimizationNotFoundException(CapacityIntelligenceException):
    def __init__(self, optimization_id: str = ""):
        super().__init__("Optimization record not found")


class HighRiskCapacityActionRequiresApprovalException(CapacityIntelligenceException):
    def __init__(self, action_name: str = ""):
        super().__init__("High-risk capacity action requires explicit human approval before execution")


class CapacityGovernanceException(CapacityIntelligenceException):
    def __init__(self, message: str = "Capacity governance evaluation error"):
        super().__init__(message)


class ImmutableCapacityIntelligenceRecordException(CapacityIntelligenceException):
    def __init__(self, record_id: str = ""):
        super().__init__("Finalized SHA-256 capacity evidence record is immutable and cannot be modified")


class CapacityDelegationException(CapacityIntelligenceException):
    def __init__(self, message: str = "Capacity delegation error"):
        super().__init__(message)


class CapacityVerificationException(CapacityIntelligenceException):
    def __init__(self, message: str = "Capacity verification error"):
        super().__init__(message)


class ForecastValidationException(CapacityIntelligenceException):
    def __init__(self, message: str = "Forecast validation error"):
        super().__init__(message)


class ResourceDependencyException(CapacityIntelligenceException):
    def __init__(self, message: str = "Resource dependency graph error"):
        super().__init__(message)


class CapacityRecommendationNotFoundException(CapacityIntelligenceException):
    def __init__(self, recommendation_id: str = ""):
        super().__init__("Capacity recommendation not found")


class CapacityIntelligenceProviderException(CapacityIntelligenceException):
    def __init__(self, provider_name: str = ""):
        super().__init__(f"Capacity intelligence provider fault isolated: {provider_name}")


class CapacityIdempotencyException(CapacityIntelligenceException):
    def __init__(self, key: str = ""):
        super().__init__("Duplicate capacity intelligence operation detected")
