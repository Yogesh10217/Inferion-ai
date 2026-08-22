"""Agent Extension Adapters for Custom Agents, Planning & Team Templates."""

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.agents.agent import Agent
from app.agents.agent_config import AgentConfig
from app.agents.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)


class AgentCapabilityManifest(BaseModel):
    """Custom Agent capability specification."""

    agent_type: str
    supported_models: List[str] = Field(default_factory=list)
    system_prompt_template: str = ""
    default_tools: List[str] = Field(default_factory=list)
    planning_strategy: str = "standard"


class AgentTemplate(BaseModel):
    """Publishable custom agent template."""

    template_id: str
    name: str
    description: str = ""
    capability_manifest: AgentCapabilityManifest


class AgentExtensionAdapter:
    """Adapts custom agent extensions for integration into AgentRegistry and PlanningEngine."""

    def __init__(self, agent_registry: Optional[AgentRegistry] = None) -> None:
        self.agent_registry = agent_registry or AgentRegistry()

    def register_custom_agent_template(
        self,
        template: AgentTemplate,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
    ) -> Agent:
        """Instantiate and register an agent from a custom agent extension template."""
        cfg = AgentConfig(
            name=template.name,
            description=template.description or template.capability_manifest.agent_type,
            system_prompt=template.capability_manifest.system_prompt_template,
            tools=template.capability_manifest.default_tools,
        )
        agent = Agent(agent_id=f"agent_{template.template_id}", config=cfg)
        self.agent_registry.register_agent(agent.agent_id, cfg)
        logger.info(f"[AGENT EXTENSION] Registered custom agent template '{template.name}' (Agent ID: {agent.agent_id})")
        return agent


