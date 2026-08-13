"""
Workflow Subsystem Exception Definitions
"""


class WorkflowError(Exception):
    """Base exception for all workflow engine errors."""
    pass


class GraphValidationError(WorkflowError):
    """Raised when DAG graph structural validation fails (e.g. cycles, missing nodes)."""
    pass


class InvalidStateTransitionError(WorkflowError):
    """Raised when an illegal workflow or node state transition is attempted."""
    pass


class NodeExecutionError(WorkflowError):
    """Raised when node execution fails."""
    def __init__(self, node_id: str, message: str, cause: Exception = None):
        super().__init__(f"Node '{node_id}' failed: {message}")
        self.node_id = node_id
        self.cause = cause


class ApprovalRequiredError(WorkflowError):
    """Raised when execution pauses waiting for human approval."""
    def __init__(self, request_id: str, message: str = "Workflow execution requires human approval"):
        super().__init__(message)
        self.request_id = request_id


class CheckpointNotFoundError(WorkflowError):
    """Raised when a requested workflow checkpoint is not found."""
    pass


class MaxIterationsExceededError(WorkflowError):
    """Raised when a loop node exceeds allowed max iterations."""
    pass


class TimeoutExceededError(WorkflowError):
    """Raised when node or workflow execution exceeds timeout limit."""
    pass


class TenantIsolationError(WorkflowError):
    """Raised when multi-tenant boundaries are violated."""
    pass


class RBACPermissionDeniedError(WorkflowError):
    """Raised when RBAC validation fails for tool/node execution."""
    pass
