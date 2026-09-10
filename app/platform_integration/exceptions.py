"""Tenant-safe exception hierarchy for Platform Integration Fabric (Phase 5.58)."""

from typing import Optional


class PlatformIntegrationException(Exception):
    """Base exception for all Platform Integration Fabric operations."""

    def __init__(self, message: str, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id
        super().__init__(message)


class CrossTenantPlatformIntegrationException(PlatformIntegrationException):
    """Raised when an illegal cross-tenant access attempt occurs. Enforces zero metadata leakage."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message)


class IntegrationContextNotFoundException(PlatformIntegrationException):
    """Raised when a requested integration context cannot be located."""
    pass


class IntegrationProviderNotFoundException(PlatformIntegrationException):
    """Raised when a specified platform provider is not registered."""
    pass


class IntegrationProviderFailureException(PlatformIntegrationException):
    """Raised when a platform provider fails or times out during intelligence collection."""
    pass


class CrossPhaseCorrelationException(PlatformIntegrationException):
    """Raised when an error occurs during cross-phase signal correlation."""
    pass


class CrossPhaseDependencyException(PlatformIntegrationException):
    """Raised when dependency resolution fails or an illegal cycle is detected."""
    pass


class IntelligenceLineageException(PlatformIntegrationException):
    """Raised when lineage graph operations or ancestry lookups fail."""
    pass


class EvidenceTraceabilityException(PlatformIntegrationException):
    """Raised when evidence reference verification or chain lookup fails."""
    pass


class DelegationTraceabilityException(PlatformIntegrationException):
    """Raised when delegation lineage or closed-loop trace cannot be resolved."""
    pass


class IntegrationLifecycleException(PlatformIntegrationException):
    """Raised when an invalid lifecycle state transition is requested."""
    pass


class HighRiskPlatformIntegrationActionRequiresApprovalException(PlatformIntegrationException):
    """Raised when a high-risk cross-phase action is executed without recorded human approval."""
    pass


class ImmutablePlatformIntegrationRecordException(PlatformIntegrationException):
    """Raised when modification is attempted on a sealed evidence record or finalized snapshot."""
    pass


class IntegrationVerificationException(PlatformIntegrationException):
    """Raised when outcome verification fails or verification criteria are violated."""
    pass


class InvalidPlatformIntegrationStateTransitionException(IntegrationLifecycleException):
    """Raised on illegal state rewind or skipping required lifecycle stages."""
    pass
