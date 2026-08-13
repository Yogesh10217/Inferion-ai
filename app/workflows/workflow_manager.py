"""
High-Level Workflow Manager Orchestrator Service
"""

from typing import Dict, Any, List, Optional
from app.workflows.workflow import WorkflowDefinition
from app.workflows.workflow_registry import WorkflowRegistry
from app.workflows.executor import WorkflowExecutor
from app.workflows.checkpoint import CheckpointManager
from app.workflows.approvals import ApprovalManager
from app.workflows.recovery import WorkflowRecoveryManager
from app.workflows.graph import WorkflowGraph
from app.workflows.dag import DAGBuilder
from app.workflows.state import WorkflowStatus
from app.workflows.exceptions import WorkflowError


class WorkflowManager:
    """Enterprise Workflow Orchestrator Service Interface."""

    def __init__(
        self,
        registry: Optional[WorkflowRegistry] = None,
        executor: Optional[WorkflowExecutor] = None,
        checkpoint_manager: Optional[CheckpointManager] = None,
        approval_manager: Optional[ApprovalManager] = None,
    ):
        self.registry = registry or WorkflowRegistry()
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.approval_manager = approval_manager or ApprovalManager()
        self.executor = executor or WorkflowExecutor(
            checkpoint_manager=self.checkpoint_manager,
            approval_manager=self.approval_manager,
        )
        self.recovery_manager = WorkflowRecoveryManager(checkpoint_manager=self.checkpoint_manager)
        self._runs_history: Dict[str, Dict[str, Any]] = {}

    def create_workflow(
        self,
        name: str,
        description: str = "",
        organization_id: str = "default_org",
        workspace_id: str = "default_workspace",
        spec: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
    ) -> WorkflowDefinition:
        """Create and register a new workflow definition."""
        graph = WorkflowGraph()
        if spec and "nodes" in spec:
            builder = DAGBuilder(graph_id=workflow_id)
            builder.add_start()
            for node_data in spec["nodes"]:
                nid = node_data.get("id") or node_data.get("node_id")
                ntype = node_data.get("type", "AGENT")
                name = node_data.get("name", nid)
                if ntype == "AGENT":
                    builder.add_agent(nid, name, agent_id=node_data.get("agent_id", "default_agent"))
                elif ntype == "TOOL":
                    builder.add_tool(nid, name, tool_name=node_data.get("tool_name", "custom_tool"))
                elif ntype == "KNOWLEDGE":
                    builder.add_knowledge(nid, name, query=node_data.get("query", ""))
                elif ntype == "APPROVAL" or ntype == "HUMAN_APPROVAL":
                    builder.add_approval(nid, name)
            builder.add_end()

            # Connect edges
            edges = spec.get("edges", [])
            if edges:
                for edge in edges:
                    builder.connect(edge["source"], edge["target"], condition=edge.get("condition"))
            else:
                # Default linear connection
                node_ids = ["START"] + [n.get("id") or n.get("node_id") for n in spec["nodes"]] + ["END"]
                for i in range(len(node_ids) - 1):
                    builder.connect(node_ids[i], node_ids[i + 1])
            graph = builder.build()
        else:
            # Default empty valid graph
            builder = DAGBuilder()
            builder.add_start().add_end().connect("START", "END")
            graph = builder.build()

        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            organization_id=organization_id,
            workspace_id=workspace_id,
            graph=graph,
        )
        return self.registry.register_workflow(workflow)

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition:
        return self.registry.get_workflow(workflow_id)

    def list_workflows(self, organization_id: Optional[str] = None) -> List[WorkflowDefinition]:
        return self.registry.list_workflows(organization_id=organization_id)

    def delete_workflow(self, workflow_id: str) -> None:
        self.registry.delete_workflow(workflow_id)

    async def run_workflow(
        self,
        workflow_id: str,
        inputs: Dict[str, Any],
        organization_id: str = "default_org",
        workspace_id: str = "default_workspace",
    ) -> Dict[str, Any]:
        """Runs workflow instance and tracks history."""
        workflow = self.get_workflow(workflow_id)
        context = {"organization_id": organization_id, "workspace_id": workspace_id}
        result = await self.executor.execute_workflow(
            workflow_id=workflow_id,
            graph=workflow.graph,
            initial_inputs=inputs,
            context=context,
        )
        run_id = result["run_id"]
        self._runs_history[run_id] = result
        return result

    async def resume_workflow(
        self,
        run_id: str,
        approval_decision: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Resumes a paused or waiting-for-approval workflow run."""
        latest_chk = self.checkpoint_manager.get_latest_checkpoint(run_id)
        workflow_id = latest_chk.variables.get("workflow_id", "default_wf")
        workflow = self.get_workflow(workflow_id)

        context = {
            "completed_nodes": latest_chk.completed_nodes,
            "variables": latest_chk.variables,
            "memory": latest_chk.memory,
            "agent_outputs": latest_chk.agent_outputs,
            "tool_outputs": latest_chk.tool_outputs,
            "approval_decision": approval_decision,
            "organization_id": latest_chk.variables.get("organization_id", "default_org"),
            "workspace_id": latest_chk.variables.get("workspace_id", "default_workspace"),
        }

        result = await self.executor.execute_workflow(
            workflow_id=workflow_id,
            graph=workflow.graph,
            initial_inputs=latest_chk.variables.get("initial_inputs", {}),
            context=context,
            run_id=run_id,
        )
        self._runs_history[run_id] = result
        return result

    def get_run_history(self, run_id: str) -> Dict[str, Any]:
        if run_id not in self._runs_history:
            # Reconstruct from checkpoints if present
            chks = self.checkpoint_manager.list_checkpoints(run_id)
            if not chks:
                raise KeyError(f"Run ID '{run_id}' not found")
            return {
                "run_id": run_id,
                "status": "PAUSED" if chks else "COMPLETED",
                "completed_nodes": chks[-1].completed_nodes,
                "checkpoints_count": len(chks),
            }
        return self._runs_history[run_id]

    def get_checkpoints(self, run_id: str) -> List[Dict[str, Any]]:
        chks = self.checkpoint_manager.list_checkpoints(run_id)
        return [chk.to_dict() for chk in chks]

    def rollback(self, run_id: str, checkpoint_id: Optional[str] = None) -> Dict[str, Any]:
        checkpoint, restored_context = self.recovery_manager.rollback(run_id, checkpoint_id)
        return {
            "status": "rolled_back",
            "checkpoint_id": checkpoint.checkpoint_id,
            "target_node": checkpoint.current_node_id,
            "context": restored_context,
        }

    def fork(self, run_id: str, checkpoint_id: Optional[str] = None) -> Dict[str, Any]:
        new_run_id, context = self.recovery_manager.fork(run_id, checkpoint_id)
        self._runs_history[new_run_id] = {"run_id": new_run_id, "status": "FORKED", "context": context}
        return {"status": "forked", "new_run_id": new_run_id, "parent_run_id": run_id}

    def get_templates(self) -> List[Dict[str, Any]]:
        return self.registry.get_templates()
