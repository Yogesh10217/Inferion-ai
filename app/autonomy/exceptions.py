"""
Exceptions for Autonomous Execution Subsystem
"""


class AutonomyException(Exception):
    """Base exception for all autonomy and worker errors."""


class ExecutionEngineError(AutonomyException):
    """Raised when execution engine encounters a fatal error."""


class CheckpointError(AutonomyException):
    """Raised when save/restore state operations fail."""


class ApprovalRequiredException(AutonomyException):
    """Raised when an operation requires explicit human approval."""

    def __init__(self, request_id: str, action: str):
        super().__init__(f"Approval required for action '{action}' (request_id: {request_id})")
        self.request_id = request_id
        self.action = action


class EmergencyStopException(AutonomyException):
    """Raised when global or tenant emergency stop is activated."""
