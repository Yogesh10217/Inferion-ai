"""
Pure Python Domain Models for Autonomous Assurance Subsystem.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class WorkflowExecutionSummary(BaseModel):
    workflow_id: str
    tenant_id: str
    title: str
    status: str
    priority: str
    plan_steps_count: int = 0
    requires_approval: bool = False
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
