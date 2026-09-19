"""Workflow Templates framework providing pre-built automations."""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.workflows.edge import Edge
from app.workflows.executor import WorkflowExecutor
from app.workflows.graph import WorkflowGraph
from app.workflows.node import AgentNode, EndNode, StartNode

logger = logging.getLogger(__name__)


class WorkflowTemplate(BaseModel):
    """Publishable Workflow Template entity."""

    template_id: str
    name: str
    category: (
        str  # 'Research Automation', 'Customer Support', 'DevOps', 'Data Analysis', 'Document Processing', 'Compliance'
    )
    description: str = ""
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    nodes_config: List[Dict[str, Any]] = Field(default_factory=list)
    edges_config: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowTemplateEngine:
    """Instantiates isolated tenant/workspace workflow instances from publishable templates."""

    def __init__(self, executor: Optional[WorkflowExecutor] = None) -> None:
        self.executor = executor or WorkflowExecutor()

    def instantiate_template(
        self,
        template: WorkflowTemplate,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> WorkflowGraph:
        """Build a DAG WorkflowGraph instance from template."""
        graph = WorkflowGraph(graph_id=f"wf_{template.template_id}")
        graph.add_node(StartNode("START"))

        for n in template.nodes_config:
            if n.get("type") == "AGENT":
                agent_id = n.get("config", {}).get("agent_id", "agent_default")
                graph.add_node(AgentNode(node_id=n["id"], name=n.get("name", n["id"]), agent_id=agent_id))

        graph.add_node(EndNode("END"))

        for e in template.edges_config:
            graph.add_edge(Edge(source_node=e["source"], target_node=e["target"]))

        logger.info(f"[WORKFLOW TEMPLATE] Instantiated template '{template.name}' for tenant '{tenant_id}'")
        return graph
