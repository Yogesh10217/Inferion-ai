"""
Workflow Lifecycle Event Definitions & Publisher Integration
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional


class WorkflowEventRegistry:
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_NODE_STARTED = "workflow.node_started"
    WORKFLOW_NODE_COMPLETED = "workflow.node_completed"
    WORKFLOW_APPROVAL_REQUESTED = "workflow.approval_requested"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_CHECKPOINT_SAVED = "workflow.checkpoint_saved"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_CANCELLED = "workflow.cancelled"


class WorkflowEventPublisher:
    """Publishes workflow lifecycle events to event bus if available."""

    def __init__(self, event_publisher: Optional[Any] = None):
        self.publisher = event_publisher

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        payload["emitted_at"] = datetime.now(timezone.utc).isoformat()
        if self.publisher and hasattr(self.publisher, "publish"):
            await self.publisher.publish(event_type, payload)
