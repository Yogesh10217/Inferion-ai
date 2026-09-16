"""Domain exceptions for Enterprise AI Architecture & Digital Twin Platform."""


class ArchitectureException(Exception):
    """Base exception for all architecture platform errors."""

    def __init__(self, message: str, tenant_id: str = "global", details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.tenant_id = tenant_id
        self.details = details or {}


class ArchitectureNodeNotFoundException(ArchitectureException):
    """Raised when an architecture node is not found."""

    def __init__(self, node_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Architecture node '{node_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id, details={"node_id": node_id})


class ArchitectureDependencyException(ArchitectureException):
    """Raised when a dependency definition or lookup fails."""


class ArchitectureCycleException(ArchitectureException):
    """Raised when a dependency cycle is detected where strictly disallowed."""


class ArchitecturePolicyViolationException(ArchitectureException):
    """Raised when an architectural rule or governance policy is violated."""


class ArchitectureChangeNotFoundException(ArchitectureException):
    """Raised when a requested architecture change proposal cannot be found."""

    def __init__(self, change_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Architecture change '{change_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id, details={"change_id": change_id})


class ArchitectureDriftException(ArchitectureException):
    """Raised when architectural drift exceeds tolerable boundaries."""


class DigitalTwinSynchronizationException(ArchitectureException):
    """Raised when digital twin reference state fails to synchronize."""


class ImpactAnalysisException(ArchitectureException):
    """Raised when blast radius or impact calculation fails."""


class ArchitectureDecisionException(ArchitectureException):
    """Raised when an architecture decision record operation fails."""


class CrossTenantArchitectureAccessException(ArchitectureException):
    """Raised when cross-tenant access to architecture metadata is attempted."""

    def __init__(self, request_tenant: str, target_tenant: str, resource_id: str) -> None:
        super().__init__(
            f"Access Denied: Tenant '{request_tenant}' cannot access architecture resource '{resource_id}' owned by tenant '{target_tenant}'.",
            tenant_id=request_tenant,
            details={"request_tenant": request_tenant, "target_tenant": target_tenant, "resource_id": resource_id},
        )


class ImmutableTopologySnapshotException(ArchitectureException):
    """Raised when attempting to mutate a finalized topology snapshot."""

    def __init__(self, snapshot_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Immutability Invariant Violation: Finalized topology snapshot '{snapshot_id}' cannot be modified.", tenant_id=tenant_id)


class ImmutableArchitectureDecisionException(ArchitectureException):
    """Raised when attempting to mutate a finalized Architecture Decision Record (ADR)."""

    def __init__(self, decision_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Immutability Invariant Violation: Finalized architecture decision record '{decision_id}' cannot be modified.", tenant_id=tenant_id)


class ArchitectureChangeIdempotencyException(ArchitectureException):
    """Raised when duplicate change submission is detected."""
