"""
Agent Handoff System Preserving Execution, Memory, and Tool Context
"""

import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.multi_agent.exceptions import HandoffError

logger = logging.getLogger(__name__)


class HandoffState(BaseModel):
    handoff_id: str
    from_agent_id: str
    to_agent_id: str
    execution_state: Dict[str, Any] = Field(default_factory=dict)
    memory_snapshot: Dict[str, Any] = Field(default_factory=dict)
    tool_context: Dict[str, Any] = Field(default_factory=dict)
    workflow_state: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class AgentHandoffManager:
    """Manages context-preserving handoffs between agents without state loss."""

    def __init__(self):
        self._handoff_records: List[HandoffState] = []

    def perform_handoff(
        self,
        from_agent_id: str,
        to_agent_id: str,
        execution_state: Dict[str, Any],
        memory_snapshot: Optional[Dict[str, Any]] = None,
        tool_context: Optional[Dict[str, Any]] = None,
        workflow_state: Optional[Dict[str, Any]] = None,
    ) -> HandoffState:
        """Transfer ownership and preserve full execution, memory, and tool context."""
        if from_agent_id == to_agent_id:
            raise HandoffError("Cannot perform handoff to the same agent")

        state = HandoffState(
            handoff_id=f"handoff_{int(time.time() * 1000)}",
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            execution_state=execution_state,
            memory_snapshot=memory_snapshot or {},
            tool_context=tool_context or {},
            workflow_state=workflow_state or {},
        )
        self._handoff_records.append(state)
        logger.info(
            f"[HANDOFF] State transferred from '{from_agent_id}' to '{to_agent_id}' (handoff: {state.handoff_id})"
        )
        return state

    def get_last_handoff(self, agent_id: str) -> Optional[HandoffState]:
        for h in reversed(self._handoff_records):
            if h.to_agent_id == agent_id or h.from_agent_id == agent_id:
                return h
        return None
