"""
High-level Agent Platform Orchestrator & Manager Service
"""

import logging
from typing import Any, Dict, Optional

from app.agents.agent import Agent
from app.agents.agent_config import AgentConfig
from app.agents.agent_context import AgentContext
from app.agents.agent_events import emit_agent_event
from app.agents.agent_factory import AgentFactory
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_session import AgentSessionManager
from app.agents.agent_state import AgentState, AgentStatus

logger = logging.getLogger(__name__)


class AgentManager:
    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        session_manager: Optional[AgentSessionManager] = None
    ):
        self.registry = registry or AgentRegistry()
        self.session_manager = session_manager or AgentSessionManager()

    def create_agent(self, agent_id: str, config_dict: Dict[str, Any]) -> AgentConfig:
        config = AgentFactory.create_custom(config_dict)
        self.registry.register_agent(agent_id, config)
        return config

    def create_agent_from_template(self, agent_id: str, template_name: str, overrides: Optional[Dict[str, Any]] = None) -> AgentConfig:
        config = AgentFactory.create_from_template(template_name, overrides)
        self.registry.register_agent(agent_id, config)
        return config

    async def run_agent(self, agent_id: str, prompt: str, context: AgentContext) -> AgentState:
        config = self.registry.get_agent(agent_id)
        state = self.session_manager.create_session(agent_id, max_iterations=config.max_iterations)

        await emit_agent_event("agent.started", context, {"agent_id": agent_id, "session_id": state.session_id, "prompt": prompt})

        agent_driver = Agent(agent_id=agent_id, config=config)
        try:
            res_state = await agent_driver.run(prompt, context, state)
            self.session_manager.update_session(res_state)
            if res_state.status == AgentStatus.COMPLETED:
                await emit_agent_event("agent.completed", context, {"agent_id": agent_id, "session_id": state.session_id})
            return res_state
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.session_manager.update_session(state)
            await emit_agent_event("agent.failed", context, {"agent_id": agent_id, "session_id": state.session_id, "error": str(e)})
            raise

    async def resume_session(self, session_id: str, approval_decision: Optional[bool] = None, context: Optional[AgentContext] = None) -> AgentState:
        state = self.session_manager.get_session(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found")

        ctx = context or AgentContext()
        config = self.registry.get_agent(state.agent_id)
        agent_driver = Agent(agent_id=state.agent_id, config=config)

        if state.status == AgentStatus.AWAITING_APPROVAL and approval_decision is not None:
            req = agent_driver.approval_controller.submit_approval(session_id, approval_decision)
            if approval_decision:
                state.status = AgentStatus.PLANNING
            else:
                state.status = AgentStatus.CANCELLED
                state.error_message = f"Tool execution rejected by user: {req.get('tool_name')}"
                self.session_manager.update_session(state)
                return state

        return await agent_driver.run(state.metadata.get("prompt", "Resume session"), ctx, state)

    async def cancel_session(self, session_id: str, context: Optional[AgentContext] = None) -> AgentState:
        state = self.session_manager.get_session(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found")
        state.status = AgentStatus.CANCELLED
        self.session_manager.update_session(state)
        ctx = context or AgentContext()
        await emit_agent_event("agent.cancelled", ctx, {"session_id": session_id})
        return state
