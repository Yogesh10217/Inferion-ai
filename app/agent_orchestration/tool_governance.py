"""Governed Tool Usage Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.exceptions import (
    AgentToolAccessDeniedException,
    CrossTenantAgentAccessException,
)


class AgentToolType(str, Enum):
    READ_ONLY = "READ_ONLY"
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    ANALYTICS = "ANALYTICS"
    POLICY_QUERY = "POLICY_QUERY"
    DELEGATED_EXECUTION = "DELEGATED_EXECUTION"
    APPROVAL_TRIGGER = "APPROVAL_TRIGGER"


class ToolPermission(BaseModel):
    required_capability: str = "READ"
    required_role: str = "TASK_EXECUTOR"
    allowed_roles: List[str] = Field(default_factory=lambda: ["TASK_EXECUTOR", "PRIMARY_PLANNER", "TEAM_SUPERVISOR"])


class ToolInvocationStatus(str, Enum):
    REQUESTED = "REQUESTED"
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class ToolAuthorization(BaseModel):
    is_authorized: bool
    reason: str
    governance_decision_id: Optional[str] = None
    requires_approval: bool = False


class ToolGovernanceResult(BaseModel):
    tool_id: str
    is_permitted: bool
    risk_score: float = 0.1
    restrictions: List[str] = Field(default_factory=list)


class AgentTool(BaseModel):
    tool_id: str = Field(default_factory=lambda: f"tool_{uuid.uuid4().hex[:10]}")
    tenant_id: str
    name: str
    tool_type: AgentToolType = AgentToolType.READ_ONLY
    target_system: str = "PLATFORM_OPERATIONS"
    data_classification: str = "INTERNAL"  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    risk_level: str = "LOW"                # LOW, MEDIUM, HIGH, CRITICAL
    is_destructive: bool = False
    permission: ToolPermission = Field(default_factory=ToolPermission)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToolInvocation(BaseModel):
    invocation_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    tool_id: str
    agent_id: str
    tenant_id: str
    task_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: ToolInvocationStatus = ToolInvocationStatus.REQUESTED
    authorization: Optional[ToolAuthorization] = None
    invoked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentToolGovernanceManager:
    """Validates tool permissions, tenant isolation, autonomy boundaries, and policy risk before invocation."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._tools: Dict[str, AgentTool] = {}
        self._invocations: Dict[str, ToolInvocation] = {}

    def register_tool(
        self,
        tenant_id: str,
        name: str,
        tool_type: AgentToolType = AgentToolType.READ_ONLY,
        target_system: str = "PLATFORM_OPERATIONS",
        data_classification: str = "INTERNAL",
        risk_level: str = "LOW",
        is_destructive: bool = False,
        required_capability: str = "READ",
        tool_id: Optional[str] = None,
    ) -> AgentTool:
        tid = tool_id or f"tool_{uuid.uuid4().hex[:10]}"
        tool = AgentTool(
            tool_id=tid,
            tenant_id=tenant_id,
            name=name,
            tool_type=tool_type,
            target_system=target_system,
            data_classification=data_classification,
            risk_level=risk_level,
            is_destructive=is_destructive,
            permission=ToolPermission(required_capability=required_capability),
        )
        self._tools[tool.tool_id] = tool
        return tool

    def get_tool(self, tool_id: str, tenant_id: str) -> AgentTool:
        tool = self._tools.get(tool_id)
        if not tool:
            raise AgentToolAccessDeniedException(f"Tool '{tool_id}' not found.")
        
        try:
            self.tenant_guard.enforce_isolation(tenant_id, tool.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, tool.tenant_id)
            
        return tool

    def authorize_tool_invocation(
        self,
        tool_id: str,
        agent_id: str,
        tenant_id: str,
        task_id: str,
        agent_capabilities: List[str],
        data_classification_allowed: List[str],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ToolInvocation:
        tool = self.get_tool(tool_id, tenant_id)

        # 1. Data classification validation
        if tool.data_classification not in data_classification_allowed and "ALL" not in data_classification_allowed:
            auth = ToolAuthorization(
                is_authorized=False,
                reason=f"Data classification '{tool.data_classification}' is not accessible by agent.",
                requires_approval=True,
            )
            inv = ToolInvocation(
                tool_id=tool_id,
                agent_id=agent_id,
                tenant_id=tenant_id,
                task_id=task_id,
                parameters=parameters or {},
                status=ToolInvocationStatus.DENIED,
                authorization=auth,
            )
            self._invocations[inv.invocation_id] = inv
            raise AgentToolAccessDeniedException(auth.reason)

        # 2. Destructive tool check -> Approval required
        requires_app = tool.is_destructive or tool.risk_level in ("HIGH", "CRITICAL")
        status = ToolInvocationStatus.AUTHORIZED if not requires_app else ToolInvocationStatus.REQUESTED

        auth = ToolAuthorization(
            is_authorized=not requires_app,
            reason="Tool authorization granted based on policy and boundary evaluation." if not requires_app else "Tool requires human approval due to risk level / destructive action.",
            governance_decision_id=f"govdec_{uuid.uuid4().hex[:8]}",
            requires_approval=requires_app,
        )

        inv = ToolInvocation(
            tool_id=tool_id,
            agent_id=agent_id,
            tenant_id=tenant_id,
            task_id=task_id,
            parameters=parameters or {},
            status=status,
            authorization=auth,
        )
        self._invocations[inv.invocation_id] = inv

        if not auth.is_authorized and not auth.requires_approval:
            raise AgentToolAccessDeniedException(auth.reason)

        return inv
