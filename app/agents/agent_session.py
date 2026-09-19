"""
Agent Session Storage & History Persistence Manager
"""

import logging
import uuid
from typing import Dict, List, Optional

from app.agents.agent_state import AgentState, AgentStatus

logger = logging.getLogger(__name__)


class AgentSessionManager:
    def __init__(self):
        self._sessions: Dict[str, AgentState] = {}

    def create_session(self, agent_id: str, max_iterations: int = 15) -> AgentState:
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        state = AgentState(
            session_id=session_id, agent_id=agent_id, status=AgentStatus.INITIALIZING, max_iterations=max_iterations
        )
        self._sessions[session_id] = state
        logger.info(f"Created agent session '{session_id}' for agent '{agent_id}'")
        return state

    def get_session(self, session_id: str) -> Optional[AgentState]:
        return self._sessions.get(session_id)

    def list_sessions(self, agent_id: Optional[str] = None) -> List[AgentState]:
        if agent_id:
            return [s for s in self._sessions.values() if s.agent_id == agent_id]
        return list(self._sessions.values())

    def update_session(self, state: AgentState) -> None:
        self._sessions[state.session_id] = state
