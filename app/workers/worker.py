"""
Digital Worker Instance Architecture
"""

import uuid
import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.workers.worker_templates import WorkerTemplate, WorkerTemplateType
from app.autonomy.execution_engine import AutonomousExecutionEngine

logger = logging.getLogger(__name__)


class DigitalWorker(BaseModel):
    worker_id: str = Field(default_factory=lambda: f"wrk_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "default_tenant"
    workspace_id: str = "default_workspace"
    template_type: WorkerTemplateType = WorkerTemplateType.CUSTOM
    capabilities: List[str] = Field(default_factory=list)
    status: str = "idle"  # idle, running, paused, terminated
    assigned_goals_count: int = 0
    created_at: float = Field(default_factory=time.time)

    async def execute_goal(self, goal_prompt: str, engine: Optional[AutonomousExecutionEngine] = None) -> Dict[str, Any]:
        """Execute a goal using the platform's autonomous execution pipeline."""
        self.status = "running"
        self.assigned_goals_count += 1
        logger.info(f"[DIGITAL WORKER] Worker '{self.worker_id}' ({self.name}) executing goal: '{goal_prompt}'")

        exec_engine = engine or AutonomousExecutionEngine()
        result = await exec_engine.execute_goal(goal_prompt, tenant_id=self.tenant_id, workspace_id=self.workspace_id)
        self.status = "idle"
        return result
