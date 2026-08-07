"""
Agent Factory
"""

from typing import Dict, Any, Optional
from app.agents.agent_config import AgentConfig
from app.agents.agent_templates import AGENT_TEMPLATES


class AgentFactory:
    @staticmethod
    def create_from_template(template_name: str, overrides: Optional[Dict[str, Any]] = None) -> AgentConfig:
        template = AGENT_TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(AGENT_TEMPLATES.keys())}")
        
        data = template.model_dump()
        if overrides:
            data.update(overrides)
        return AgentConfig(**data)

    @staticmethod
    def create_custom(config_dict: Dict[str, Any]) -> AgentConfig:
        return AgentConfig(**config_dict)
