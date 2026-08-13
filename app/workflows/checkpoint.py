"""
Workflow Checkpointing & Snapshot Manager
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.workflows.exceptions import CheckpointNotFoundError


class WorkflowCheckpoint:
    """Represents an immutable snapshot of a workflow execution state."""

    def __init__(
        self,
        run_id: str,
        current_node_id: str,
        completed_nodes: List[str],
        variables: Dict[str, Any],
        memory: Dict[str, Any],
        agent_outputs: Dict[str, Any],
        tool_outputs: Dict[str, Any],
        checkpoint_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.checkpoint_id = checkpoint_id or f"chk_{uuid.uuid4().hex[:12]}"
        self.run_id = run_id
        self.current_node_id = current_node_id
        self.completed_nodes = list(completed_nodes)
        self.variables = dict(variables)
        self.memory = dict(memory)
        self.agent_outputs = dict(agent_outputs)
        self.tool_outputs = dict(tool_outputs)
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "run_id": self.run_id,
            "current_node_id": self.current_node_id,
            "completed_nodes": self.completed_nodes,
            "variables": self.variables,
            "memory": self.memory,
            "agent_outputs": self.agent_outputs,
            "tool_outputs": self.tool_outputs,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowCheckpoint":
        return cls(
            checkpoint_id=data["checkpoint_id"],
            run_id=data["run_id"],
            current_node_id=data["current_node_id"],
            completed_nodes=data.get("completed_nodes", []),
            variables=data.get("variables", {}),
            memory=data.get("memory", {}),
            agent_outputs=data.get("agent_outputs", {}),
            tool_outputs=data.get("tool_outputs", {}),
            created_at=data.get("created_at"),
        )


class CheckpointManager:
    """In-memory & DB backed checkpoint store for saving, retrieving, and restoring workflow snapshots."""

    def __init__(self):
        self._checkpoints: Dict[str, List[WorkflowCheckpoint]] = {}  # run_id -> list of checkpoints

    def save_checkpoint(
        self,
        run_id: str,
        current_node_id: str,
        completed_nodes: List[str],
        variables: Dict[str, Any],
        memory: Dict[str, Any],
        agent_outputs: Dict[str, Any],
        tool_outputs: Dict[str, Any],
    ) -> WorkflowCheckpoint:
        checkpoint = WorkflowCheckpoint(
            run_id=run_id,
            current_node_id=current_node_id,
            completed_nodes=completed_nodes,
            variables=variables,
            memory=memory,
            agent_outputs=agent_outputs,
            tool_outputs=tool_outputs,
        )
        if run_id not in self._checkpoints:
            self._checkpoints[run_id] = []
        self._checkpoints[run_id].append(checkpoint)
        return checkpoint

    def get_latest_checkpoint(self, run_id: str) -> WorkflowCheckpoint:
        checkpoints = self._checkpoints.get(run_id, [])
        if not checkpoints:
            raise CheckpointNotFoundError(f"No checkpoints found for run_id '{run_id}'")
        return checkpoints[-1]

    def get_checkpoint(self, run_id: str, checkpoint_id: str) -> WorkflowCheckpoint:
        checkpoints = self._checkpoints.get(run_id, [])
        for chk in checkpoints:
            if chk.checkpoint_id == checkpoint_id:
                return chk
        raise CheckpointNotFoundError(f"Checkpoint '{checkpoint_id}' not found for run_id '{run_id}'")

    def list_checkpoints(self, run_id: str) -> List[WorkflowCheckpoint]:
        return self._checkpoints.get(run_id, [])
