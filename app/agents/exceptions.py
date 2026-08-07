"""
Agent Framework Exceptions
"""

class AgentError(Exception):
    """Base exception for all agent errors."""
    pass

class AgentNotFoundError(AgentError):
    """Raised when an agent definition is not found."""
    pass

class ToolError(AgentError):
    """Base exception for tool execution issues."""
    pass

class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""
    pass

class ToolExecutionError(ToolError):
    """Raised when a tool execution fails."""
    pass

class ToolPermissionDeniedError(ToolError):
    """Raised when RBAC or tenant scopes deny tool execution."""
    pass

class PlanningError(AgentError):
    """Raised when planning fails."""
    pass

class MaxIterationsReachedError(AgentError):
    """Raised when agent execution loop reaches maximum allowed iterations."""
    pass

class BudgetExceededException(AgentError):
    """Raised when token or financial budget limits are exceeded."""
    pass

class ApprovalRequiredException(AgentError):
    """Raised when an action requires human approval before proceeding."""
    pass

class CheckpointError(AgentError):
    """Raised when session state serialization or restoration fails."""
    pass

class ReflectionError(AgentError):
    """Raised when reflection or self-critique fails."""
    pass
