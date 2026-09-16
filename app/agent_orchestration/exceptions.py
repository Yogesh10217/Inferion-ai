"""Domain Exceptions for Enterprise AI Agent Orchestration Platform (Phase 5.36)."""

from app.platform_contracts.exceptions import CrossTenantAccessException


class AgentOrchestrationException(Exception):
    """Base exception for all Agent Orchestration Platform errors."""

    def __init__(self, message: str = "An error occurred in Agent Orchestration Platform.") -> None:
        super().__init__(message)
        self.message = message


class CrossTenantAgentAccessException(CrossTenantAccessException, AgentOrchestrationException):
    """Raised when cross-tenant agent resource access is attempted.

    CRITICAL: Must leak ZERO metadata (no resource existence, agent names, task IDs, timestamps, or state).
    """

    def __init__(self, requester_tenant_id: str = "unknown", resource_tenant_id: str = "unknown") -> None:
        opaque_msg = "Access denied or resource not found in tenant context."
        CrossTenantAccessException.__init__(self, "opaque", "opaque")
        self.message = opaque_msg
        self.args = (opaque_msg,)


class AgentNotFoundException(AgentOrchestrationException):
    """Raised when an agent is not found."""

    def __init__(self, agent_id: str = "unknown") -> None:
        super().__init__(f"Agent '{agent_id}' was not found.")
        self.agent_id = agent_id


class AgentTaskNotFoundException(AgentOrchestrationException):
    """Raised when an agent task is not found."""

    def __init__(self, task_id: str = "unknown") -> None:
        super().__init__(f"Agent task '{task_id}' was not found.")
        self.task_id = task_id


class AgentPlanNotFoundException(AgentOrchestrationException):
    """Raised when an agent plan is not found."""

    def __init__(self, plan_id: str = "unknown") -> None:
        super().__init__(f"Agent plan '{plan_id}' was not found.")
        self.plan_id = plan_id


class AgentExecutionNotFoundException(AgentOrchestrationException):
    """Raised when an agent execution session is not found."""

    def __init__(self, execution_id: str = "unknown") -> None:
        super().__init__(f"Agent execution '{execution_id}' was not found.")
        self.execution_id = execution_id


class AgentCapabilityViolationException(AgentOrchestrationException):
    """Raised when an agent attempts an operation outside its assigned capabilities."""

    def __init__(self, message: str = "Agent capability violation detected.") -> None:
        super().__init__(message)


class AgentAutonomyViolationException(AgentOrchestrationException):
    """Raised when an agent attempts to exceed its explicit autonomy boundary."""

    def __init__(self, message: str = "Agent autonomy boundary exceeded.") -> None:
        super().__init__(message)


class AgentToolAccessDeniedException(AgentOrchestrationException):
    """Raised when access to a tool is denied based on policy, risk, or authorization."""

    def __init__(self, message: str = "Tool access denied by governance policy.") -> None:
        super().__init__(message)


class AgentPolicyViolationException(AgentOrchestrationException):
    """Raised when an agent action violates enterprise governance policies."""

    def __init__(self, message: str = "Agent action violates enterprise policy.") -> None:
        super().__init__(message)


class AgentExecutionBlockedException(AgentOrchestrationException):
    """Raised when agent execution is blocked by runtime safeguards or policies."""

    def __init__(self, message: str = "Agent execution is blocked.") -> None:
        super().__init__(message)


class AgentDelegationBlockedException(AgentOrchestrationException):
    """Raised when delegated execution cannot proceed."""

    def __init__(self, message: str = "Delegated execution request blocked.") -> None:
        super().__init__(message)


class InvalidAgentExecutionTransitionException(AgentOrchestrationException):
    """Raised when an invalid task or execution state transition is requested."""

    def __init__(self, current_state: str, target_state: str) -> None:
        super().__init__(f"Invalid transition from state '{current_state}' to '{target_state}'.")
        self.current_state = current_state
        self.target_state = target_state


class ImmutableAgentExecutionException(AgentOrchestrationException):
    """Raised when an attempt is made to mutate a finalized immutable execution trace."""

    def __init__(self, message: str = "Cannot mutate finalized agent execution record.") -> None:
        super().__init__(message)


class AgentCollaborationException(AgentOrchestrationException):
    """Raised when a multi-agent collaboration error occurs."""

    def __init__(self, message: str = "Multi-agent collaboration failed.") -> None:
        super().__init__(message)


class AgentBudgetExceededException(AgentOrchestrationException):
    """Raised when an agent exceeds its allocated financial or resource budget."""

    def __init__(self, message: str = "Agent budget limit exceeded.") -> None:
        super().__init__(message)


class AgentRuntimeLimitExceededException(AgentOrchestrationException):
    """Raised when an agent runtime limit (max steps, max duration, recursion) is exceeded."""

    def __init__(self, message: str = "Agent runtime limit exceeded.") -> None:
        super().__init__(message)


class HighRiskAgentActionRequiresApprovalException(AgentOrchestrationException):
    """Raised when a high-risk or destructive action requires human approval."""

    def __init__(self, message: str = "High-risk action requires human approval before execution.") -> None:
        super().__init__(message)
