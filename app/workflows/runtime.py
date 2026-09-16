"""
Workflow Engine Unified Runtime Facade
"""

from typing import Optional

from app.workflows.scheduler import WorkflowScheduler
from app.workflows.workflow_manager import WorkflowManager


class WorkflowRuntime:
    """Unified Facade for Enterprise Workflow Engine Subsystem."""

    def __init__(self, manager: Optional[WorkflowManager] = None):
        self.manager = manager or WorkflowManager()
        self.executor = self.manager.executor
        self.checkpoint_manager = self.manager.checkpoint_manager
        self.approval_manager = self.manager.approval_manager
        self.scheduler = WorkflowScheduler(self.executor)

    def get_manager(self) -> WorkflowManager:
        return self.manager
