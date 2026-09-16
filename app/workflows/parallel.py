"""
Parallel Path Execution Engine (asyncio.gather)
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Tuple

from app.workflows.exceptions import NodeExecutionError
from app.workflows.node import BaseNode


class ParallelExecutor:
    """Executes multiple workflow node execution paths concurrently."""

    @staticmethod
    async def execute_parallel(
        nodes: List[BaseNode],
        context: Dict[str, Any],
        executor_fn: Callable[[BaseNode, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Runs node execution tasks concurrently using asyncio.gather.
        Returns a dictionary mapping node_id -> node_output.
        """
        if not nodes:
            return {}

        async def run_single_node(node: BaseNode) -> Tuple[str, Dict[str, Any]]:
            output = await executor_fn(node, context)
            return node.node_id, output

        tasks = [run_single_node(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged_outputs: Dict[str, Dict[str, Any]] = {}
        errors: List[Exception] = []

        for res in results:
            if isinstance(res, Exception):
                errors.append(res)
            elif isinstance(res, tuple):
                node_id, out = res
                merged_outputs[node_id] = out

        if errors:
            raise NodeExecutionError(
                node_id="parallel_batch",
                message=f"Parallel execution encountered {len(errors)} error(s): {errors[0]}",
                cause=errors[0]
            )

        return merged_outputs
