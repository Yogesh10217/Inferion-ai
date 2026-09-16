"""Tenant-safe exceptions for Integration Intelligence Platform (Phase 5.40)."""


class IntegrationIntelligenceException(Exception):
    """Base exception for all Integration Intelligence errors."""

    def __init__(self, message: str = "Integration Intelligence error occurred.") -> None:
        super().__init__(message)
        self.message = message


class CrossTenantIntegrationAccessException(IntegrationIntelligenceException):
    """Exception raised when a cross-tenant boundary violation occurs.

    MUST leak ZERO metadata:
    - no tenant identifiers
    - no connector identifiers
    - no workflow identifiers
    - no integration metadata
    - no resource existence information
    """

    def __init__(self, message: str = "Access denied.") -> None:
        super().__init__("Access denied.")


class IntegrationNotFoundException(IntegrationIntelligenceException):
    """Raised when integration is not found."""

    def __init__(self, integration_id: str) -> None:
        super().__init__(f"Integration '{integration_id}' not found.")
        self.integration_id = integration_id


class InvalidAccessStateTransitionException(IntegrationIntelligenceException):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, current_state: str, target_state: str) -> None:
        super().__init__(f"Invalid state transition from '{current_state}' to '{target_state}'.")
        self.current_state = current_state
        self.target_state = target_state


class ConnectorNotFoundException(IntegrationIntelligenceException):
    """Raised when connector is not found."""

    def __init__(self, connector_id: str) -> None:
        super().__init__(f"Connector '{connector_id}' not found.")
        self.connector_id = connector_id


class WorkflowNotFoundException(IntegrationIntelligenceException):
    """Raised when workflow is not found."""

    def __init__(self, workflow_id: str) -> None:
        super().__init__(f"Integration workflow '{workflow_id}' not found.")
        self.workflow_id = workflow_id


class IntegrationExecutionNotFoundException(IntegrationIntelligenceException):
    """Raised when execution is not found."""

    def __init__(self, execution_id: str) -> None:
        super().__init__(f"Integration execution '{execution_id}' not found.")
        self.execution_id = execution_id


class IntegrationPolicyViolationException(IntegrationIntelligenceException):
    """Raised when integration policy is violated."""

    def __init__(self, policy_id: str, reason: str) -> None:
        super().__init__(f"Integration policy '{policy_id}' violated: {reason}")
        self.policy_id = policy_id
        self.reason = reason


class ConnectorAccessDeniedException(IntegrationIntelligenceException):
    """Raised when connector access is denied."""

    def __init__(self, connector_id: str, reason: str) -> None:
        super().__init__(f"Connector '{connector_id}' access denied: {reason}")
        self.connector_id = connector_id
        self.reason = reason


class IntegrationExecutionBlockedException(IntegrationIntelligenceException):
    """Raised when workflow execution is blocked by governance."""

    def __init__(self, execution_id: str, reason: str) -> None:
        super().__init__(f"Integration execution '{execution_id}' blocked: {reason}")
        self.execution_id = execution_id
        self.reason = reason


class IntegrationValidationException(IntegrationIntelligenceException):
    """Raised when workflow or mapping validation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Integration validation failed: {reason}")
        self.reason = reason


class IntegrationFailureException(IntegrationIntelligenceException):
    """Raised when integration execution fails."""

    def __init__(self, execution_id: str, error_message: str) -> None:
        super().__init__(f"Integration execution '{execution_id}' failed: {error_message}")
        self.execution_id = execution_id
        self.error_message = error_message


class IntegrationRetryException(IntegrationIntelligenceException):
    """Raised when integration retry policy is violated or retry limit exceeded."""

    def __init__(self, attempt_count: int, max_retries: int) -> None:
        super().__init__(f"Integration retry limit exceeded ({attempt_count}/{max_retries}). Sent to dead-letter handler.")
        self.attempt_count = attempt_count
        self.max_retries = max_retries


class IntegrationDelegationBlockedException(IntegrationIntelligenceException):
    """Raised when integration delegation is blocked."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Integration delegation blocked: {reason}")
        self.reason = reason


class ImmutableIntegrationRecordException(IntegrationIntelligenceException):
    """Raised when attempting to mutate an immutable finalized integration record."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Integration record '{record_id}' is finalized and immutable.")
        self.record_id = record_id


class HighRiskIntegrationRequiresApprovalException(IntegrationIntelligenceException):
    """Raised when high-risk integration action requires explicit human approval."""

    def __init__(self, action_name: str, risk_score: float) -> None:
        super().__init__(f"High-risk integration action '{action_name}' (risk: {risk_score}) requires human approval.")
        self.action_name = action_name
        self.risk_score = risk_score


class IntegrationDependencyException(IntegrationIntelligenceException):
    """Raised when integration dependency check fails or target system is unreachable."""

    def __init__(self, dependency_id: str, reason: str) -> None:
        super().__init__(f"Integration dependency '{dependency_id}' failure: {reason}")
        self.dependency_id = dependency_id
        self.reason = reason
