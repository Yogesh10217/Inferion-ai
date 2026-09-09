"""Tenant-safe exception hierarchy for Reliability Intelligence (Phase 5.55)."""

class ReliabilityIntelligenceException(Exception):
    """Base exception for all Reliability Intelligence operations."""
    def __init__(self, message: str = "Reliability intelligence operation failed"):
        super().__init__(message)


class CrossTenantReliabilityIntelligenceException(ReliabilityIntelligenceException):
    """Raised when cross-tenant access is attempted. Exposes zero metadata."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message)


class ReliabilityAssessmentNotFoundException(ReliabilityIntelligenceException):
    """Raised when a reliability assessment is not found."""
    def __init__(self, record_id: str = "Record not found"):
        super().__init__(f"Reliability assessment not found: {record_id}")


class ServiceHealthNotFoundException(ReliabilityIntelligenceException):
    """Raised when a service health record is not found."""
    def __init__(self, service_id: str = "Service health record not found"):
        super().__init__(f"Service health record not found: {service_id}")


class DependencyNotFoundException(ReliabilityIntelligenceException):
    """Raised when a dependency node or relationship is not found."""
    def __init__(self, dep_id: str = "Dependency not found"):
        super().__init__(f"Dependency record not found: {dep_id}")


class FailurePredictionNotFoundException(ReliabilityIntelligenceException):
    """Raised when a failure prediction is not found."""
    def __init__(self, pred_id: str = "Prediction not found"):
        super().__init__(f"Failure prediction record not found: {pred_id}")


class FailurePropagationException(ReliabilityIntelligenceException):
    """Raised when failure propagation analysis fails."""
    pass


class ReliabilityStateNotFoundException(ReliabilityIntelligenceException):
    """Raised when a reliability lifecycle state is not found."""
    pass


class InvalidReliabilityStateTransitionException(ReliabilityIntelligenceException):
    """Raised when an invalid lifecycle state transition is attempted."""
    def __init__(self, current: str, target: str):
        super().__init__(f"Invalid reliability state transition from '{current}' to '{target}'")


class ResilienceAssessmentException(ReliabilityIntelligenceException):
    """Raised when resilience assessment fails."""
    pass


class RecoveryReadinessException(ReliabilityIntelligenceException):
    """Raised when recovery readiness analysis fails."""
    pass


class DegradationPlanningException(ReliabilityIntelligenceException):
    """Raised when safe degradation planning fails."""
    pass


class HighRiskReliabilityActionRequiresApprovalException(ReliabilityIntelligenceException):
    """Raised when a high-risk reliability action requires human approval."""
    def __init__(self, action_id: str = "Action requires human approval"):
        super().__init__(f"High-risk reliability action requires human approval: {action_id}")


class ChaosExperimentGovernanceException(ReliabilityIntelligenceException):
    """Raised when a chaos experiment proposal violates governance or risk boundaries."""
    pass


class ReliabilityDelegationException(ReliabilityIntelligenceException):
    """Raised when delegation creation or coordination fails."""
    pass


class ReliabilityVerificationException(ReliabilityIntelligenceException):
    """Raised when post-remediation reliability verification fails."""
    pass


class ImmutableReliabilityRecordException(ReliabilityIntelligenceException):
    """Raised when an attempt is made to modify a sealed immutable reliability record."""
    def __init__(self, record_id: str = "Record is immutable"):
        super().__init__(f"Cannot modify immutable reliability record: {record_id}")


class ReliabilityGovernanceException(ReliabilityIntelligenceException):
    """Raised when governance evaluation blocks a reliability action."""
    pass


class ReliabilityCapacityException(ReliabilityIntelligenceException):
    """Raised when capacity exhaustion or risk threshold is breached."""
    pass
