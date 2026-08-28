"""Domain Exceptions for Platform Resilience Subsystem (Phase 5.37)."""

from typing import Optional
from app.platform_contracts.exceptions import CrossTenantAccessException


class PlatformResilienceException(Exception):
    """Base exception for all Platform Resilience Platform errors."""

    def __init__(self, message: str = "An error occurred in Platform Resilience Subsystem.") -> None:
        super().__init__(message)
        self.message = message


class CrossTenantResilienceAccessException(CrossTenantAccessException, PlatformResilienceException):
    """Raised when cross-tenant resilience resource access is attempted.
    
    CRITICAL: Must leak ZERO metadata (no resource existence, metadata, region info, infrastructure IDs, timestamps, or topology).
    """

    def __init__(self, requester_tenant_id: str = "unknown", resource_tenant_id: str = "unknown") -> None:
        opaque_msg = "Access denied or resource not found in tenant context."
        CrossTenantAccessException.__init__(self, "opaque", "opaque")
        self.message = opaque_msg
        self.args = (opaque_msg,)


class ResilienceResourceNotFoundException(PlatformResilienceException):
    """Raised when a resilience resource is not found."""

    def __init__(self, resource_id: str = "unknown") -> None:
        super().__init__(f"Resilience resource '{resource_id}' was not found.")
        self.resource_id = resource_id


class CapacityLimitExceededException(PlatformResilienceException):
    """Raised when infrastructure or service capacity limit is exceeded."""

    def __init__(self, message: str = "Capacity limit exceeded.") -> None:
        super().__init__(message)


class InvalidFailoverTransitionException(PlatformResilienceException):
    """Raised when an invalid failover state machine transition is attempted."""

    def __init__(self, current_state: str, target_state: str) -> None:
        super().__init__(f"Invalid failover transition from state '{current_state}' to '{target_state}'.")
        self.current_state = current_state
        self.target_state = target_state


class DisasterRecoveryBlockedException(PlatformResilienceException):
    """Raised when disaster recovery activation or execution is blocked by policy or governance."""

    def __init__(self, message: str = "Disaster recovery action is blocked.") -> None:
        super().__init__(message)


class RecoveryPlanNotFoundException(PlatformResilienceException):
    """Raised when a recovery plan is not found."""

    def __init__(self, plan_id: str = "unknown") -> None:
        super().__init__(f"Recovery plan '{plan_id}' was not found.")
        self.plan_id = plan_id


class RecoveryVerificationFailedException(PlatformResilienceException):
    """Raised when recovery or failover outcome verification fails."""

    def __init__(self, message: str = "Recovery outcome verification failed.") -> None:
        super().__init__(message)


class ResiliencePolicyViolationException(PlatformResilienceException):
    """Raised when a resilience action violates enterprise policies."""

    def __init__(self, message: str = "Action violates platform resilience governance policy.") -> None:
        super().__init__(message)


class ImmutableResilienceRecordException(PlatformResilienceException):
    """Raised when an attempt is made to mutate a finalized immutable resilience record."""

    def __init__(self, message: str = "Cannot mutate finalized immutable resilience record.") -> None:
        super().__init__(message)


class ResilienceDelegationBlockedException(PlatformResilienceException):
    """Raised when a delegated resilience execution request is blocked."""

    def __init__(self, message: str = "Delegated resilience action blocked.") -> None:
        super().__init__(message)


class HighRiskRecoveryRequiresApprovalException(PlatformResilienceException):
    """Raised when a high-risk recovery, failover, or DR action requires human approval."""

    def __init__(self, message: str = "High-risk resilience operation requires human approval.") -> None:
        super().__init__(message)


class DependencyFailureException(PlatformResilienceException):
    """Raised when a critical service dependency failure is detected."""

    def __init__(self, dependency_id: str = "unknown", details: str = "") -> None:
        super().__init__(f"Dependency failure on '{dependency_id}': {details}")
        self.dependency_id = dependency_id


class CircuitBreakerOpenException(PlatformResilienceException):
    """Raised when an action is attempted while a circuit breaker is in OPEN state."""

    def __init__(self, breaker_id: str = "unknown") -> None:
        super().__init__(f"Circuit breaker '{breaker_id}' is OPEN. Requests blocked.")
        self.breaker_id = breaker_id


class BulkheadCapacityExceededException(PlatformResilienceException):
    """Raised when workload partition bulkhead capacity is exhausted."""

    def __init__(self, partition_id: str = "unknown") -> None:
        super().__init__(f"Bulkhead partition '{partition_id}' capacity exhausted.")
        self.partition_id = partition_id
