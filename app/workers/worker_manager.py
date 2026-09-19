"""
Digital Worker Manager & Coordinator
"""

import logging
from typing import Any, Dict, List, Optional

from app.autonomy.execution_engine import AutonomousExecutionEngine
from app.workers.worker import DigitalWorker
from app.workers.worker_templates import WorkerTemplate, WorkerTemplateType

logger = logging.getLogger(__name__)


class WorkerManager:
    """Manages digital worker instances across tenants."""

    def __init__(self, execution_engine: Optional[AutonomousExecutionEngine] = None):
        self._workers: Dict[str, DigitalWorker] = {}
        self.execution_engine = execution_engine or AutonomousExecutionEngine()

    def create_worker(
        self,
        name: str,
        template_type: str = "custom",
        tenant_id: str = "default_tenant",
        workspace_id: str = "default_workspace",
    ) -> DigitalWorker:
        ttype = (
            WorkerTemplateType(template_type)
            if template_type in [t.value for t in WorkerTemplateType]
            else WorkerTemplateType.CUSTOM
        )
        preset = WorkerTemplate.get_preset(ttype)

        worker = DigitalWorker(
            name=name,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            template_type=ttype,
            capabilities=preset.capabilities,
        )
        self._workers[worker.worker_id] = worker
        logger.info(f"[WORKER MANAGER] Created worker '{worker.worker_id}' ({name})")
        return worker

    def get_worker(self, worker_id: str) -> Optional[DigitalWorker]:
        return self._workers.get(worker_id)

    def list_workers(self, tenant_id: str = "default_tenant") -> List[DigitalWorker]:
        return [w for w in self._workers.values() if w.tenant_id in (tenant_id, "global", "default_tenant")]

    async def assign_goal(self, worker_id: str, goal_prompt: str) -> Dict[str, Any]:
        worker = self.get_worker(worker_id)
        if not worker:
            raise ValueError(f"Digital Worker '{worker_id}' not found")
        return await worker.execute_goal(goal_prompt, engine=self.execution_engine)

    def terminate_worker(self, worker_id: str) -> bool:
        if worker_id in self._workers:
            self._workers[worker_id].status = "terminated"
            logger.info(f"[WORKER MANAGER] Terminated worker '{worker_id}'")
            return True
        return False

    def monitor_worker(self, worker_id: str) -> Dict[str, Any]:
        worker = self.get_worker(worker_id)
        if not worker:
            raise ValueError(f"Digital Worker '{worker_id}' not found")
        return {
            "worker_id": worker.worker_id,
            "name": worker.name,
            "status": worker.status,
            "assigned_goals_count": worker.assigned_goals_count,
            "capabilities": worker.capabilities,
        }
