"""
Agent Definition Repository & Registry
"""

import logging
from typing import Dict, Any, Optional, List
from app.agents.agent_config import AgentConfig
from app.agents.exceptions import AgentNotFoundError

logger = logging.getLogger(__name__)


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentConfig] = {}

    def register_agent(self, agent_id: str, config: AgentConfig) -> None:
        self._agents[agent_id] = config
        logger.info(f"Registered agent '{agent_id}' ({config.name})")

    def get_agent(self, agent_id: str) -> AgentConfig:
        config = self._agents.get(agent_id)
        if not config:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found in registry")
        return config

    def list_agents(self) -> Dict[str, AgentConfig]:
        return dict(self._agents)

    def delete_agent(self, agent_id: str) -> None:
        if agent_id in self._agents:
            del self._agents[agent_id]
