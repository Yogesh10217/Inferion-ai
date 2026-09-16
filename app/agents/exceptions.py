"""
Agent Framework Exceptions
"""


class AgentError(Exception):
    """Base exception for all agent errors."""


class AgentNotFoundError(AgentError):
    """Raised when an agent definition is not found."""


class ToolError(AgentError):
    """Base exception for tool execution issues."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""


class ToolExecutionError(ToolError):
    """Raised when a tool execution fails."""


class ToolPermissionDeniedError(ToolError):
    """Raised when RBAC or tenant scopes deny tool execution."""


class PlanningError(AgentError):
    """Raised when planning fails."""


class MaxIterationsReachedError(AgentError):
    """Raised when agent execution loop reaches maximum allowed iterations."""


class BudgetExceededException(AgentError):
    """Raised when token or financial budget limits are exceeded."""


class ApprovalRequiredException(AgentError):
    """Raised when an action requires human approval before proceeding."""


class CheckpointError(AgentError):
    """Raised when session state serialization or restoration fails."""


class ReflectionError(AgentError):
    """Raised when reflection or self-critique fails."""
