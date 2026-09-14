"""
Workflow Graph Data Structure & DAG Topological Processor
"""

from typing import Dict, List, Optional, Any
from app.workflows.node import BaseNode, NodeType
from app.workflows.edge import Edge
from app.workflows.exceptions import GraphValidationError


class WorkflowGraph:
    """Directed Acyclic Graph (DAG) representation of a Workflow."""

    def __init__(self, graph_id: Optional[str] = None):
        self.graph_id = graph_id
        self.nodes: Dict[str, BaseNode] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[str, List[Edge]] = {}
        self.in_edges: Dict[str, List[Edge]] = {}

    def add_node(self, node: BaseNode) -> None:
        """Add a node to the graph."""
        if node.node_id in self.nodes:
            raise GraphValidationError(f"Duplicate node_id '{node.node_id}' in graph")
        self.nodes[node.node_id] = node
        if node.node_id not in self.adjacency:
            self.adjacency[node.node_id] = []
        if node.node_id not in self.in_edges:
            self.in_edges[node.node_id] = []

    def add_edge(self, edge: Edge) -> None:
        """Add a directed edge between two existing nodes."""
        if edge.source_node not in self.nodes:
            raise GraphValidationError(f"Source node '{edge.source_node}' does not exist in graph")
        if edge.target_node not in self.nodes:
            raise GraphValidationError(f"Target node '{edge.target_node}' does not exist in graph")

        self.edges.append(edge)
        self.adjacency[edge.source_node].append(edge)
        self.in_edges[edge.target_node].append(edge)

    def get_start_nodes(self) -> List[BaseNode]:
        """Find start nodes (explicit START type or nodes with 0 in-degree)."""
        start_nodes = [node for node in self.nodes.values() if node.node_type == NodeType.START]
        if not start_nodes:
            start_nodes = [
                node for node_id, node in self.nodes.items()
                if len(self.in_edges.get(node_id, [])) == 0
            ]
        return start_nodes

    def get_end_nodes(self) -> List[BaseNode]:
        """Find end nodes (explicit END type or nodes with 0 out-degree)."""
        end_nodes = [node for node in self.nodes.values() if node.node_type == NodeType.END]
        if not end_nodes:
            end_nodes = [
                node for node_id, node in self.nodes.items()
                if len(self.adjacency.get(node_id, [])) == 0
            ]
        return end_nodes

    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        """Get outgoing edges from node sorted by priority (highest priority first)."""
        edges = self.adjacency.get(node_id, [])
        return sorted(edges, key=lambda e: e.priority, reverse=True)

    def get_incoming_edges(self, node_id: str) -> List[Edge]:
        return self.in_edges.get(node_id, [])

    def validate(self) -> None:
        """
        Validates graph integrity:
        1. Non-empty graph.
        2. Validate individual nodes.
        3. Ensure START and END nodes exist or can be determined.
        4. Cycle detection using Kahn's algorithm (topological sort).
        """
        if not self.nodes:
            raise GraphValidationError("Graph contains no nodes")

        for node_id, node in self.nodes.items():
            errors = node.validate()
            if errors:
                raise GraphValidationError(f"Node '{node_id}' validation errors: {', '.join(errors)}")

        start_nodes = self.get_start_nodes()
        if not start_nodes:
            raise GraphValidationError("Graph has no valid starting node")

        # Kahn's Algorithm for cycle detection and topological ordering validation
        in_degree: Dict[str, int] = {node_id: len(self.in_edges.get(node_id, [])) for node_id in self.nodes}
        queue = [node_id for node_id, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for edge in self.adjacency.get(curr, []):
                target = edge.target_node
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)

        if visited_count < len(self.nodes):
            raise GraphValidationError("Graph contains cycles (not a valid DAG)")

    def get_topological_order(self) -> List[str]:
        """Return node_ids in topologically sorted order."""
        self.validate()
        in_degree: Dict[str, int] = {node_id: len(self.in_edges.get(node_id, [])) for node_id in self.nodes}
        queue = [node_id for node_id, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for edge in self.get_outgoing_edges(curr):
                target = edge.target_node
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)

        return order

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "nodes": [node.checkpoint() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
        }
