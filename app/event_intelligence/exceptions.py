"""Enterprise AI Event Intelligence Domain Exceptions (Phase 5.34)."""


class EventIntelligenceException(Exception):
    """Base exception for all Event Intelligence Platform errors."""
    pass


class CrossTenantEventAccessException(EventIntelligenceException):
    """Raised when cross-tenant event or context access is attempted."""
    def __init__(self, requesting_tenant: str, target_tenant: str) -> None:
        super().__init__(
            f"Access denied: Tenant '{requesting_tenant}' cannot access resources belonging to tenant '{target_tenant}'."
        )


class EventNotFoundException(EventIntelligenceException):
    """Raised when an enterprise event is not found."""
    def __init__(self, event_id: str) -> None:
        super().__init__(f"Enterprise event '{event_id}' not found.")


class InvalidEventException(EventIntelligenceException):
    """Raised when an enterprise event payload or metadata is invalid."""
    pass


class EventSchemaValidationException(EventIntelligenceException):
    """Raised when an event fails schema validation during normalization."""
    pass


class DuplicateEventException(EventIntelligenceException):
    """Raised when a duplicate event is processed or idempotency conflict occurs."""
    pass


class EventCorrelationException(EventIntelligenceException):
    """Raised when event correlation analysis encounters an error."""
    pass


class EventAutomationBlockedException(EventIntelligenceException):
    """Raised when an event automation plan or execution is blocked by governance/policy."""
    pass


class EventPolicyViolationException(EventIntelligenceException):
    """Raised when an event or response violates platform policy."""
    pass


class ImmutableEventRecordException(EventIntelligenceException):
    """Raised when attempting to mutate a finalized immutable event record or snapshot."""
    def __init__(self, resource_id: str) -> None:
        super().__init__(f"Cannot mutate finalized immutable event resource '{resource_id}'.")


class EventDelegationBlockedException(EventIntelligenceException):
    """Raised when an event response delegation request is blocked."""
    pass


class EventResolutionException(EventIntelligenceException):
    """Raised when an invalid event resolution lifecycle transition is attempted."""
    pass


class EventSourceNotRegisteredException(EventIntelligenceException):
    """Raised when an event source is not registered in the EventSourceRegistry."""
    def __init__(self, source_id: str) -> None:
        super().__init__(f"Event source '{source_id}' is not registered.")


class EventCausalityException(EventIntelligenceException):
    """Raised when causality analysis fails or encounters invalid nodes."""
    pass


class HighRiskAutomationRequiresApprovalException(EventIntelligenceException):
    """Raised when a high-risk automation requires human approval before proceeding."""
    def __init__(self, rule_id: str) -> None:
        super().__init__(f"High-risk automation rule '{rule_id}' requires explicit human approval.")
