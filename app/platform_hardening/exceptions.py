"""
Tenant-safe exception hierarchy for Platform Hardening, Integration Audits & Assurance Certification.
"""


class PlatformHardeningException(Exception):
    """Base exception for platform hardening and auditing operations."""

    def __init__(self, message: str = "Platform hardening exception occurred."):
        super().__init__(message)
        self.message = message


class CrossTenantPlatformHardeningException(PlatformHardeningException):
    """Tenant isolation violation exception. Never leaks metadata across tenant boundaries."""

    def __init__(self, message: str = "Access denied"):
        # Always enforce generic message to prevent metadata leakage
        super().__init__("Access denied")


class CrossPhaseIntegrationException(PlatformHardeningException):
    """Raised when cross-phase integration contracts fail."""
    pass


class ProviderIntegrationException(PlatformHardeningException):
    """Raised when a provider integration fails."""
    pass


class ProviderTimeoutException(ProviderIntegrationException):
    """Raised when a provider operation times out."""
    pass


class ProviderContractViolationException(ProviderIntegrationException):
    """Raised when a provider violates its declared protocol contract."""
    pass


class IntegrationContractViolationException(CrossPhaseIntegrationException):
    """Raised when integration payload contracts are violated."""
    pass


class TracePropagationException(PlatformHardeningException):
    """Raised when trace context is dropped, mutated, or corrupted across phases."""
    pass


class ContextPropagationException(PlatformHardeningException):
    """Raised when context attributes (tenant_id, trace_id, correlation_id) are lost."""
    pass


class LineageIntegrityException(PlatformHardeningException):
    """Raised when intelligence lineage edges are orphaned, missing, or cyclic."""
    pass


class EvidenceIntegrityException(PlatformHardeningException):
    """Raised when evidence hash verification fails or evidence is tampered."""
    pass


class ImmutablePlatformAuditRecordException(PlatformHardeningException):
    """Raised when attempting to modify a finalized, SHA-256 sealed audit record."""
    def __init__(self, message: str = "Cannot modify sealed immutable audit record."):
        super().__init__(message)


class StubDetectionException(PlatformHardeningException):
    """Raised when an unclassified production stub is detected in active production path."""
    pass


class DeadCodeDetectionException(PlatformHardeningException):
    """Raised when dead code analysis detects critical abandoned components."""
    pass


class DuplicateContractException(PlatformHardeningException):
    """Raised when duplicate models, schemas, or contracts are detected across phases."""
    pass


class CircularDependencyException(PlatformHardeningException):
    """Raised when circular dependencies are detected in subsystem graphs."""
    pass


class DisconnectedEngineException(PlatformHardeningException):
    """Raised when an engine is instantiated but disconnected from pipeline execution."""
    pass


class ManagerIntegrationException(PlatformHardeningException):
    """Raised when a subsystem manager violates orchestration or isolation contracts."""
    pass


class RepositoryIsolationException(PlatformHardeningException):
    """Raised when repository thread safety or tenant boundary isolation fails."""
    pass


class ConcurrencyValidationException(PlatformHardeningException):
    """Raised when concurrent operations result in race conditions or lost updates."""
    pass


class IdempotencyValidationException(PlatformHardeningException):
    """Raised when deduplication fails for idempotent requests."""
    pass


class GovernanceValidationException(PlatformHardeningException):
    """Raised when human approval gates or governance rules are bypassed."""
    pass


class DelegationValidationException(PlatformHardeningException):
    """Raised when delegation requests attempt direct execution or bypass auto_execute=False."""
    pass


class VerificationValidationException(PlatformHardeningException):
    """Raised when execution verification feedback loop fails to report to assurance."""
    pass


class PlatformCertificationException(PlatformHardeningException):
    """Raised when platform certification criteria are failed."""
    pass
