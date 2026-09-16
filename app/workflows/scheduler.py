"""
Workflow Scheduler for Async Background Execution
"""

import asyncio
from typing import Any, Dict, Optional

from app.workflows.executor import WorkflowExecutor
from app.workflows.graph import WorkflowGraph


class WorkflowScheduler:
    """Schedules background workflow execution tasks."""

    def __init__(self, executor: WorkflowExecutor):
        self.executor = executor
        self._background_tasks: Dict[str, asyncio.Task] = {}

    def schedule_run(
        self,
        workflow_id: str,
        graph: WorkflowGraph,
        initial_inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """Schedules a workflow run in the background and returns run_id immediately."""
        run_id = run_id or f"run_{asyncio.get_event_loop().time()}"

        task = asyncio.create_task(
            self.executor.execute_workflow(
                workflow_id=workflow_id,
                graph=graph,
                initial_inputs=initial_inputs,
                context=context,
                run_id=run_id,
            )
        )
        self._background_tasks[run_id] = task
        return run_id

    def cancel_scheduled_run(self, run_id: str) -> bool:
        task = self._background_tasks.get(run_id)
        if task and not task.done():
            task.cancel()
            return True
        return False
