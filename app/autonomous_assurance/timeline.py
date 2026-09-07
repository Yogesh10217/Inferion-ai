"""
Workflow Timeline & Chronological Audit Subsystem.
Tracks chronological events throughout the workflow lifecycle.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class WorkflowTimelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"wfevt_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    event_type: str
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AutonomousWorkflowTimeline(BaseModel):
    timeline_id: str = Field(default_factory=lambda: f"time_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    events: List[WorkflowTimelineEvent] = Field(default_factory=list)


class WorkflowTimelineEngine:
    """Manages workflow timeline audit events."""

    def __init__(self) -> None:
        self._timelines: Dict[str, AutonomousWorkflowTimeline] = {}

    def add_event(self, workflow_id: str, tenant_id: str, event_type: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> WorkflowTimelineEvent:
        if workflow_id not in self._timelines:
            self._timelines[workflow_id] = AutonomousWorkflowTimeline(workflow_id=workflow_id, tenant_id=tenant_id)

        evt = WorkflowTimelineEvent(
            workflow_id=workflow_id,
            event_type=event_type,
            description=description,
            metadata=metadata or {},
        )
        self._timelines[workflow_id].events.append(evt)
        return evt

    def get_timeline(self, workflow_id: str) -> Optional[AutonomousWorkflowTimeline]:
        return self._timelines.get(workflow_id)
