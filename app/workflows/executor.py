"""
Workflow DAG Execution Engine
"""

import asyncio
import time
from typing import Dict, Any, Optional, Set

from app.workflows.graph import WorkflowGraph
from app.workflows.node import BaseNode, NodeType
from app.workflows.state import WorkflowStatus, NodeStatus
from app.workflows.exceptions import (
    NodeExecutionError, ApprovalRequiredError, TenantIsolationError
)
from app.workflows.checkpoint import CheckpointManager
from app.workflows.approvals import ApprovalManager
from app.workflows.conditions import ConditionalExecutor
from app.workflows.events import WorkflowEventPublisher, WorkflowEventRegistry
from app.tracing.span_factory import SpanFactory


class WorkflowExecutor:
    """Core DAG Execution Engine."""

    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager] = None,
        approval_manager: Optional[ApprovalManager] = None,
        event_publisher: Optional[WorkflowEventPublisher] = None,
        metrics_service: Optional[Any] = None,
    ):
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.approval_manager = approval_manager or ApprovalManager()
        self.event_publisher = event_publisher or WorkflowEventPublisher()
        self.metrics_service = metrics_service

    async def execute_workflow(
        self,
        workflow_id: str,
        graph: WorkflowGraph,
        initial_inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Runs workflow graph execution to completion or pause point."""
        run_id = run_id or f"run_{int(time.time() * 1000)}"
        exec_context = context or {}
        exec_context.update({
            "workflow_id": workflow_id,
            "run_id": run_id,
            "initial_inputs": initial_inputs,
            "variables": dict(initial_inputs),
            "memory": exec_context.get("memory", {}),
            "agent_outputs": exec_context.get("agent_outputs", {}),
            "tool_outputs": exec_context.get("tool_outputs", {}),
            "node_outputs": exec_context.get("node_outputs", {}),
            "organization_id": exec_context.get("organization_id", "default_org"),
            "workspace_id": exec_context.get("workspace_id", "default_workspace"),
        })

        graph.validate()
        topological_order = graph.get_topological_order()

        completed_nodes: Set[str] = set(exec_context.get("completed_nodes", []))
        node_outputs: Dict[str, Any] = exec_context.get("node_outputs", {})

        await self.event_publisher.publish(WorkflowEventRegistry.WORKFLOW_STARTED, {"workflow_id": workflow_id, "run_id": run_id})

        wf_span = SpanFactory.create_workflow_start_span(workflow_id, run_id)
        status = WorkflowStatus.RUNNING

        try:
            for node_id in topological_order:
                if node_id in completed_nodes:
                    continue

                node = graph.nodes[node_id]

                # Check if incoming edges conditions pass
                in_edges = graph.get_incoming_edges(node_id)
                if in_edges:
                    active_edges = ConditionalExecutor.select_active_edges(in_edges, exec_context)
                    if not active_edges and node.node_type not in (NodeType.START, NodeType.END, NodeType.JOIN):
                        # Skip node if no incoming conditions pass
                        node.status = NodeStatus.SKIPPED
                        continue

                # Execute step with retries
                await self.event_publisher.publish(
                    WorkflowEventRegistry.WORKFLOW_NODE_STARTED,
                    {"workflow_id": workflow_id, "run_id": run_id, "node_id": node_id}
                )

                node_span = SpanFactory.create_workflow_node_span(workflow_id, run_id, node_id, node.node_type.value)
                try:
                    output = await self._execute_node_with_retry(node, exec_context)
                finally:
                    node_span.end()

                node_outputs[node_id] = output
                exec_context["node_outputs"] = node_outputs
                exec_context["variables"].update(output if isinstance(output, dict) else {"result": output})
                completed_nodes.add(node_id)

                # Save checkpoint at node boundary
                self.checkpoint_manager.save_checkpoint(
                    run_id=run_id,
                    current_node_id=node_id,
                    completed_nodes=list(completed_nodes),
                    variables=exec_context["variables"],
                    memory=exec_context["memory"],
                    agent_outputs=exec_context["agent_outputs"],
                    tool_outputs=exec_context["tool_outputs"],
                )

                await self.event_publisher.publish(
                    WorkflowEventRegistry.WORKFLOW_NODE_COMPLETED,
                    {"workflow_id": workflow_id, "run_id": run_id, "node_id": node_id}
                )

            status = WorkflowStatus.COMPLETED
            await self.event_publisher.publish(
                WorkflowEventRegistry.WORKFLOW_COMPLETED,
                {"workflow_id": workflow_id, "run_id": run_id, "status": status.value}
            )
            wf_span.end()

            return {
                "status": status.value,
                "run_id": run_id,
                "workflow_id": workflow_id,
                "node_outputs": node_outputs,
                "variables": exec_context["variables"],
                "completed_nodes": list(completed_nodes),
            }

        except ApprovalRequiredError as e:
            status = WorkflowStatus.WAITING_FOR_APPROVAL
            appr_span = SpanFactory.create_workflow_approval_span(workflow_id, run_id, e.request_id)
            appr_span.end()
            wf_span.end()
            self.approval_manager.create_request(
                run_id=run_id,
                node_id=e.request_id.split("_")[1] if "_" in e.request_id else "approval",
                workflow_id=workflow_id,
                prompt=str(e),
            )
            await self.event_publisher.publish(
                WorkflowEventRegistry.WORKFLOW_APPROVAL_REQUESTED,
                {"workflow_id": workflow_id, "run_id": run_id, "request_id": e.request_id}
            )
            return {
                "status": status.value,
                "run_id": run_id,
                "workflow_id": workflow_id,
                "approval_request_id": e.request_id,
                "completed_nodes": list(completed_nodes),
                "variables": exec_context["variables"],
            }

        except Exception as e:
            status = WorkflowStatus.FAILED
            wf_span.record_exception(e)
            wf_span.end()
            await self.event_publisher.publish(
                WorkflowEventRegistry.WORKFLOW_FAILED,
                {"workflow_id": workflow_id, "run_id": run_id, "error": str(e)}
            )
            return {
                "status": status.value,
                "run_id": run_id,
                "workflow_id": workflow_id,
                "error": str(e),
                "completed_nodes": list(completed_nodes),
            }

    async def _execute_node_with_retry(self, node: BaseNode, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a single node with retry logic."""
        attempt = 0
        max_retries = max(0, node.max_retries)

        while True:
            try:
                if node.timeout and node.timeout > 0:
                    return await asyncio.wait_for(node.execute(context), timeout=node.timeout)
                else:
                    return await node.execute(context)
            except (ApprovalRequiredError, TenantIsolationError):
                raise
            except Exception as e:
                attempt += 1
                if attempt > max_retries:
                    node.status = NodeStatus.FAILED
                    node.error = str(e)
                    raise NodeExecutionError(node.node_id, f"Exceeded {max_retries} retries: {e}", cause=e)
                await asyncio.sleep(node.retry_delay)
