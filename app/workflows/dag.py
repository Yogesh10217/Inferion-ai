"""
DAG Validation & Graph Builder Utilities
"""

from typing import Dict, Any, List, Optional
from app.workflows.graph import WorkflowGraph
from app.workflows.node import (
    BaseNode, NodeType, StartNode, EndNode, AgentNode, ToolNode,
    HumanApprovalNode, ConditionNode, ParallelNode, JoinNode,
    KnowledgeNode, WebhookNode, DelayNode, CustomNode
)
from app.workflows.edge import Edge
from app.workflows.exceptions import GraphValidationError


class DAGBuilder:
    """Builder utility for constructing valid WorkflowGraph DAGs."""

    def __init__(self, graph_id: Optional[str] = None):
        self.graph = WorkflowGraph(graph_id=graph_id)

    def add_start(self, node_id: str = "START", name: str = "Start") -> "DAGBuilder":
        self.graph.add_node(StartNode(node_id=node_id, name=name))
        return self

    def add_end(self, node_id: str = "END", name: str = "End") -> "DAGBuilder":
        self.graph.add_node(EndNode(node_id=node_id, name=name))
        return self

    def add_agent(
        self,
        node_id: str,
        name: str,
        agent_id: str,
        role: str = "general",
        config: Optional[Dict[str, Any]] = None
    ) -> "DAGBuilder":
        self.graph.add_node(AgentNode(node_id=node_id, name=name, agent_id=agent_id, role=role, config=config))
        return self

    def add_tool(
        self,
        node_id: str,
        name: str,
        tool_name: str,
        tool_type: str = "custom",
        config: Optional[Dict[str, Any]] = None
    ) -> "DAGBuilder":
        self.graph.add_node(ToolNode(node_id=node_id, name=name, tool_name=tool_name, tool_type=tool_type, config=config))
        return self

    def add_approval(
        self,
        node_id: str,
        name: str,
        approver_role: str = "approver",
        config: Optional[Dict[str, Any]] = None
    ) -> "DAGBuilder":
        self.graph.add_node(HumanApprovalNode(node_id=node_id, name=name, approver_role=approver_role, config=config))
        return self

    def add_condition(
        self,
        node_id: str,
        name: str,
        condition_expression: str = "True",
        config: Optional[Dict[str, Any]] = None
    ) -> "DAGBuilder":
        self.graph.add_node(ConditionNode(node_id=node_id, name=name, condition_expression=condition_expression, config=config))
        return self

    def add_parallel(
        self,
        node_id: str,
        name: str,
        branch_nodes: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> "DAGBuilder":
        self.graph.add_node(ParallelNode(node_id=node_id, name=name, branch_nodes=branch_nodes, config=config))
        return self

    def add_join(self, node_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> "DAGBuilder":
        self.graph.add_node(JoinNode(node_id=node_id, name=name, config=config))
        return self

    def add_knowledge(
        self,
        node_id: str,
        name: str,
        action: str = "search",
        query: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> "DAGBuilder":
        self.graph.add_node(KnowledgeNode(node_id=node_id, name=name, action=action, query=query, config=config))
        return self

    def add_node(self, node: BaseNode) -> "DAGBuilder":
        self.graph.add_node(node)
        return self

    def connect(
        self,
        source_id: str,
        target_id: str,
        condition: Optional[str] = None,
        priority: int = 0
    ) -> "DAGBuilder":
        self.graph.add_edge(Edge(source_node=source_id, target_node=target_id, condition=condition, priority=priority))
        return self

    def build(self) -> WorkflowGraph:
        self.graph.validate()
        return self.graph


def validate_dag_spec(spec: Dict[str, Any]) -> None:
    """Validates raw dictionary graph specification."""
    if not isinstance(spec, dict):
        raise GraphValidationError("DAG specification must be a dictionary")
    if "nodes" not in spec or not isinstance(spec["nodes"], list):
        raise GraphValidationError("DAG specification must contain a 'nodes' list")
    if len(spec["nodes"]) == 0:
        raise GraphValidationError("DAG specification contains empty nodes")
