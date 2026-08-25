"""Shared Domain-Neutral Platform Contract Exceptions (Phase 5.30)."""


class PlatformContractException(Exception):
    """Base exception for all platform contract errors."""

    def __init__(self, message: str, code: str = "PLATFORM_CONTRACT_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class CrossTenantAccessException(PlatformContractException):
    """Raised on cross-tenant access attempts. Safe error: leaks zero metadata."""

    def __init__(self, requested_tenant: str, owner_tenant: str):
        super().__init__(
            f"Access denied: Resource belongs to tenant '{owner_tenant}', requested by '{requested_tenant}'. Zero metadata leaked.",
            code="CROSS_TENANT_ACCESS_DENIED",
        )


class ImmutableMutationException(PlatformContractException):
    """Raised when mutation is attempted on a finalized immutable resource."""

    def __init__(self, resource_id: str):
        super().__init__(
            f"Resource '{resource_id}' is finalized and immutable. Mutation operation rejected.",
            code="IMMUTABLE_MUTATION_DENIED",
        )


class IdempotencyConflictException(PlatformContractException):
    """Raised when identical idempotency_key is submitted with a different payload fingerprint."""

    def __init__(self, idempotency_key: str, operation_type: str):
        super().__init__(
            f"Idempotency conflict for key '{idempotency_key}' on operation '{operation_type}': payload fingerprint mismatch.",
            code="IDEMPOTENCY_CONFLICT",
        )


class InvalidLifecycleTransitionException(PlatformContractException):
    """Raised when an illegal state transition is attempted in a lifecycle machine."""

    def __init__(self, current_state: str, target_state: str):
        super().__init__(
            f"Invalid lifecycle transition from '{current_state}' to '{target_state}'.",
            code="INVALID_LIFECYCLE_TRANSITION",
        )


class CircularDependencyException(PlatformContractException):
    """Raised when a circular import or circular manager dependency chain is detected."""

    def __init__(self, cycle_path: str):
        super().__init__(
            f"Circular dependency violation detected: {cycle_path}",
            code="CIRCULAR_DEPENDENCY_DETECTED",
        )


class ContractVersionException(PlatformContractException):
    """Raised when an incompatible or invalid contract version is encountered."""

    def __init__(self, current_version: str, expected_range: str):
        super().__init__(
            f"Contract version '{current_version}' incompatible with expected range '{expected_range}'.",
            code="CONTRACT_VERSION_INCOMPATIBLE",
        )
