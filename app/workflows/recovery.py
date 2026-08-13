"""
Workflow Recovery, Rollback, Replay, and Fork Capabilities
"""

import uuid
from typing import Dict, Any, Tuple, Optional
from app.workflows.checkpoint import CheckpointManager, WorkflowCheckpoint
from app.workflows.exceptions import WorkflowError, CheckpointNotFoundError


class WorkflowRecoveryManager:
    """Manages workflow recovery, rollback, replay, and run forking."""

    def __init__(self, checkpoint_manager: CheckpointManager):
        self.checkpoint_manager = checkpoint_manager

    def rollback(self, run_id: str, checkpoint_id: Optional[str] = None) -> Tuple[WorkflowCheckpoint, Dict[str, Any]]:
        """
        Rolls back execution state to a specified checkpoint (or latest if unspecified).
        Returns the target checkpoint and restored execution context.
        """
        if checkpoint_id:
            checkpoint = self.checkpoint_manager.get_checkpoint(run_id, checkpoint_id)
        else:
            checkpoint = self.checkpoint_manager.get_latest_checkpoint(run_id)

        restored_context = {
            "run_id": checkpoint.run_id,
            "current_node_id": checkpoint.current_node_id,
            "completed_nodes": list(checkpoint.completed_nodes),
            "variables": dict(checkpoint.variables),
            "memory": dict(checkpoint.memory),
            "agent_outputs": dict(checkpoint.agent_outputs),
            "tool_outputs": dict(checkpoint.tool_outputs),
            "is_recovery": True,
        }
        return checkpoint, restored_context

    def fork(self, run_id: str, checkpoint_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Forks a workflow run from a checkpoint into a new independent run context.
        Returns (new_run_id, new_context).
        """
        checkpoint, context = self.rollback(run_id, checkpoint_id)
        new_run_id = f"run_{uuid.uuid4().hex[:12]}"
        context["run_id"] = new_run_id
        context["parent_run_id"] = run_id
        context["forked_from_checkpoint"] = checkpoint.checkpoint_id

        # Save initial checkpoint for forked run
        self.checkpoint_manager.save_checkpoint(
            run_id=new_run_id,
            current_node_id=checkpoint.current_node_id,
            completed_nodes=checkpoint.completed_nodes,
            variables=checkpoint.variables,
            memory=checkpoint.memory,
            agent_outputs=checkpoint.agent_outputs,
            tool_outputs=checkpoint.tool_outputs,
        )
        return new_run_id, context
