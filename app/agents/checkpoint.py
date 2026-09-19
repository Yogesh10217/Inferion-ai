"""
Agent Session Checkpoint & Recovery Manager
"""

import logging
import time
from typing import Any, Dict, Optional

from app.agents.agent_state import AgentState
from app.agents.exceptions import CheckpointError

logger = logging.getLogger(__name__)


class CheckpointManager:
    def __init__(self):
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    def save_checkpoint(self, session_id: str, state: AgentState, checkpoint_name: Optional[str] = None) -> str:
        try:
            name = checkpoint_name or f"cp_{int(time.time() * 1000)}"
            key = f"{session_id}:{name}"
            serialized_state = state.model_dump()
            self._checkpoints[key] = {
                "session_id": session_id,
                "name": name,
                "timestamp": time.time(),
                "state": serialized_state,
            }
            logger.info(f"Saved checkpoint '{name}' for session '{session_id}'")
            return name
        except Exception as e:
            raise CheckpointError(f"Failed to save checkpoint: {e}")

    def load_checkpoint(self, session_id: str, checkpoint_name: str) -> AgentState:
        key = f"{session_id}:{checkpoint_name}"
        cp = self._checkpoints.get(key)
        if not cp:
            raise CheckpointError(f"Checkpoint '{checkpoint_name}' for session '{session_id}' not found")
        try:
            return AgentState(**cp["state"])
        except Exception as e:
            raise CheckpointError(f"Failed to restore checkpoint state: {e}")

    def list_checkpoints(self, session_id: str) -> Dict[str, Any]:
        prefix = f"{session_id}:"
        results = {}
        for key, cp in self._checkpoints.items():
            if key.startswith(prefix):
                results[cp["name"]] = cp["timestamp"]
        return results
