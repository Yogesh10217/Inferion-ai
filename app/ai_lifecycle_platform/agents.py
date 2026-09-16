"""AI Agent Registry & Autonomy Governance Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import AgentNotFoundException, CrossTenantLifecycleAccessException


class AgentType(str, Enum):
    TASK_AGENT = "TASK_AGENT"
    ORCHESTRATOR = "ORCHESTRATOR"
    REASONING_AGENT = "REASONING_AGENT"
    TOOL_AGENT = "TOOL_AGENT"
    AUTONOMOUS_WORKER = "AUTONOMOUS_WORKER"


class AgentAutonomyLevel(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    ASSISTED = "ASSISTED"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    SUPERVISED = "SUPERVISED"
    LIMITED_AUTONOMOUS = "LIMITED_AUTONOMOUS"


class AgentStatus(str, Enum):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class AgentCapabilityReference(BaseModel):
    capability_name: str
    description: str = ""


class AgentToolReference(BaseModel):
    tool_id: str
    tool_name: str
    requires_approval: bool = False


class AgentVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: f"agver_{uuid.uuid4().hex[:12]}")
    version_tag: str = "1.0.0"
    autonomy_level: AgentAutonomyLevel = AgentAutonomyLevel.HUMAN_APPROVED
    tools: List[AgentToolReference] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIAgent(BaseModel):
    agent_id: str = Field(default_factory=lambda: f"ag_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    agent_type: AgentType = AgentType.TASK_AGENT
    autonomy_level: AgentAutonomyLevel = AgentAutonomyLevel.HUMAN_APPROVED
    status: AgentStatus = AgentStatus.REGISTERED
    versions: List[AgentVersion] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentManager:
    """Manages AI Agent registry, versioning, and autonomy governance evaluation requirements."""

    def __init__(self) -> None:
        self._agents: Dict[str, AIAgent] = {}

    def register_agent(
        self,
        tenant_id: str,
        name: str,
        agent_type: AgentType = AgentType.TASK_AGENT,
        autonomy_level: AgentAutonomyLevel = AgentAutonomyLevel.HUMAN_APPROVED,
        tools: Optional[List[AgentToolReference]] = None,
    ) -> AIAgent:
        aver = AgentVersion(autonomy_level=autonomy_level, tools=tools or [])
        ag = AIAgent(
            tenant_id=tenant_id,
            name=name,
            agent_type=agent_type,
            autonomy_level=autonomy_level,
            versions=[aver],
        )
        self._agents[ag.agent_id] = ag
        return ag

    def requires_governance_evaluation(self, agent: AIAgent) -> bool:
        """High autonomy agents (SUPERVISED or LIMITED_AUTONOMOUS) mandate explicit governance evaluation."""
        return agent.autonomy_level in (AgentAutonomyLevel.SUPERVISED, AgentAutonomyLevel.LIMITED_AUTONOMOUS)

    def get_agent(self, agent_id: str, tenant_id: str) -> AIAgent:
        ag = self._agents.get(agent_id)
        if not ag:
            raise AgentNotFoundException(agent_id)
        if tenant_id != "global" and ag.tenant_id != "global" and tenant_id != ag.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, ag.tenant_id)
        return ag

    def list_agents(self, tenant_id: str) -> List[AIAgent]:
        return [a for a in self._agents.values() if a.tenant_id == tenant_id]
