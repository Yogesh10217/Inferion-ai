"""
Workflow Core Domain Definition & Configuration
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.workflows.graph import WorkflowGraph
from app.workflows.state import WorkflowStatus


class WorkflowDefinition:
    """Represents a full workflow graph definition and metadata."""

    def __init__(
        self,
        workflow_id: Optional[str] = None,
        name: str = "Untitled Workflow",
        description: str = "",
        organization_id: str = "default_org",
        workspace_id: str = "default_workspace",
        version: int = 1,
        status: WorkflowStatus = WorkflowStatus.READY,
        graph: Optional[WorkflowGraph] = None,
        config: Optional[Dict[str, Any]] = None,
        created_by: str = "system",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.workflow_id = workflow_id or f"wf_{uuid.uuid4().hex[:12]}"
        self.name = name
        self.description = description
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.version = version
        self.status = status
        self.graph = graph or WorkflowGraph(graph_id=self.workflow_id)
        self.config = config or {}
        self.created_by = created_by
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "organization_id": self.organization_id,
            "workspace_id": self.workspace_id,
            "version": self.version,
            "status": self.status.value,
            "graph": self.graph.to_dict(),
            "config": self.config,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
