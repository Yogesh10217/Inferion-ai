"""
Conditional Execution Engine & Branch Evaluator
"""

from typing import Dict, Any, List
from app.workflows.edge import Edge


class ConditionalExecutor:
    """Evaluates graph edge conditions against current workflow execution context."""

    @staticmethod
    def evaluate_edge(edge: Edge, context: Dict[str, Any]) -> bool:
        """Evaluates a single edge condition."""
        return edge.evaluate_condition(context)

    @staticmethod
    def select_active_edges(edges: List[Edge], context: Dict[str, Any]) -> List[Edge]:
        """Filters a list of outgoing edges to select those whose conditions evaluate to True."""
        active_edges = []
        for edge in edges:
            if edge.evaluate_condition(context):
                active_edges.append(edge)
        return active_edges
