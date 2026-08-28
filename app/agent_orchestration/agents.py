"""Enterprise Agent Registry Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.exceptions import (
    AgentNotFoundException,
    CrossTenantAgentAccessException,
)


class AgentType(str, Enum):
    GENERAL = "GENERAL"
    PLANNER = "PLANNER"
    EXECUTOR = "EXECUTOR"
    SUPERVISOR = "SUPERVISOR"
    SPECIALIST = "SPECIALIST"
    ANALYST = "ANALYST"
    SECURITY = "SECURITY"
    RELIABILITY = "RELIABILITY"
    KNOWLEDGE = "KNOWLEDGE"
    DECISION = "DECISION"
    AUTOMATION = "AUTOMATION"


class AgentStatus(str, Enum):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"
    MAINTENANCE = "MAINTENANCE"


class AgentCapabilityType(str, Enum):
    READ = "READ"
    ANALYZE = "ANALYZE"
    PLAN = "PLAN"
    RECOMMEND = "RECOMMEND"
    DELEGATE = "DELEGATE"
    EXECUTE_WITH_APPROVAL = "EXECUTE_WITH_APPROVAL"


class AgentRole(str, Enum):
    PRIMARY_PLANNER = "PRIMARY_PLANNER"
    TASK_EXECUTOR = "TASK_EXECUTOR"
    TEAM_SUPERVISOR = "TEAM_SUPERVISOR"
    DOMAIN_SPECIALIST = "DOMAIN_SPECIALIST"
    SECURITY_AUDITOR = "SECURITY_AUDITOR"
    RELIABILITY_MONITOR = "RELIABILITY_MONITOR"
    ANALYST = "ANALYST"


class AgentVersion(BaseModel):
    version: str = "1.0.0"
    governed_model_version_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentMetadata(BaseModel):
    description: str = ""
    owner_email: str = "system@enterprise.internal"
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)


class AgentReference(BaseModel):
    agent_id: str
    tenant_id: str
    agent_type: AgentType
    version: str = "1.0.0"


class EnterpriseAgent(BaseModel):
    agent_id: str = Field(default_factory=lambda: f"agent_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    agent_type: AgentType = AgentType.GENERAL
    status: AgentStatus = AgentStatus.ACTIVE
    capabilities: List[str] = Field(default_factory=list)  # Capability IDs or Names
    autonomy_policy_id: Optional[str] = None
    role: AgentRole = AgentRole.TASK_EXECUTOR
    version: AgentVersion = Field(default_factory=AgentVersion)
    metadata: AgentMetadata = Field(default_factory=AgentMetadata)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentManager:
    """Manages Enterprise Agent registrations, retrieval, and status updates."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._agents: Dict[str, EnterpriseAgent] = {}

    def register_agent(
        self,
        tenant_id: str,
        name: str,
        agent_type: AgentType = AgentType.GENERAL,
        role: AgentRole = AgentRole.TASK_EXECUTOR,
        capabilities: Optional[List[str]] = None,
        autonomy_policy_id: Optional[str] = None,
        description: str = "",
        governed_model_version_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        agent_id: Optional[str] = None,
    ) -> EnterpriseAgent:
        new_id = agent_id or f"agent_{uuid.uuid4().hex[:12]}"
        agent = EnterpriseAgent(
            agent_id=new_id,
            tenant_id=tenant_id,
            name=name,
            agent_type=agent_type,
            role=role,
            capabilities=capabilities or [],
            autonomy_policy_id=autonomy_policy_id,
            version=AgentVersion(version="1.0.0", governed_model_version_id=governed_model_version_id),
            metadata=AgentMetadata(description=description, tags=tags or []),
        )
        self._agents[agent.agent_id] = agent
        return agent

    def get_agent(self, agent_id: str, tenant_id: str) -> EnterpriseAgent:
        agent = self._agents.get(agent_id)
        if not agent:
            raise AgentNotFoundException(agent_id)
        
        try:
            self.tenant_guard.enforce_isolation(tenant_id, agent.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, agent.tenant_id)
        
        return agent

    def list_agents(
        self,
        tenant_id: str,
        agent_type: Optional[AgentType] = None,
        status: Optional[AgentStatus] = None,
    ) -> List[EnterpriseAgent]:
        results = []
        for agent in self._agents.values():
            if agent.tenant_id == tenant_id or tenant_id == "global":
                if agent_type and agent.agent_type != agent_type:
                    continue
                if status and agent.status != status:
                    continue
                results.append(agent)
        return results

    def update_agent_status(self, agent_id: str, tenant_id: str, new_status: AgentStatus) -> EnterpriseAgent:
        agent = self.get_agent(agent_id, tenant_id)
        agent.status = new_status
        agent.updated_at = datetime.now(timezone.utc)
        return agent
