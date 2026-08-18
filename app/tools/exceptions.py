"""
Exceptions for Enterprise Tool Calling & MCP Platform Subsystem
"""

class ToolException(Exception):
    """Base exception for all tool subsystem errors."""
    pass

class ToolNotFoundException(ToolException):
    """Raised when a requested tool is not registered or found."""
    pass

class ToolExecutionException(ToolException):
    """Raised when tool execution fails or raises an error."""
    pass

class ToolValidationError(ToolException):
    """Raised when tool parameter or schema validation fails."""
    pass

class ToolPermissionDenied(ToolException):
    """Raised when RBAC, tenant isolation, or policy checks fail."""
    pass

class ToolRateLimitExceeded(ToolException):
    """Raised when execution violates rate limit constraints."""
    pass

class ToolTimeoutException(ToolExecutionException):
    """Raised when tool execution times out."""
    pass

class ToolApprovalRequiredException(ToolPermissionDenied):
    """Raised when a high-risk tool action requires manual or workflow approval."""
    def __init__(self, message: str, execution_id: str, tool_name: str):
        super().__init__(message)
        self.execution_id = execution_id
        self.tool_name = tool_name

class MCPException(ToolException):
    """Base exception for Model Context Protocol (MCP) errors."""
    pass

class MCPConnectionError(MCPException):
    """Raised when connecting to or communicating with an MCP server fails."""
    pass

class MCPToolError(MCPException):
    """Raised when an MCP tool execution fails."""
    pass

class MCPResourceError(MCPException):
    """Raised when an MCP resource access fails."""
    pass

class MCPPromptError(MCPException):
    """Raised when an MCP prompt operation fails."""
    pass
