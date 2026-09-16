"""Defensive Analytical Attack Graph Model."""

import logging
from typing import Dict, List, Set

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AttackNode(BaseModel):
    node_id: str
    asset_id: str
    asset_name: str
    asset_type: str
    risk_weight: float = 1.0


class AttackEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str  # CALLS, ACCESSES, DEPENDS_ON, STORES_SECRETS_FOR
    propagation_factor: float = 0.5


class AnalyticalAttackGraph:
    """Defensive analytical graph mapping asset exposure pathways and risk propagation."""

    def __init__(self) -> None:
        self._nodes: Dict[str, AttackNode] = {}
        self._edges: List[AttackEdge] = []

    def add_node(self, node_id: str, asset_id: str, asset_name: str, asset_type: str, risk_weight: float = 1.0) -> AttackNode:
        node = AttackNode(
            node_id=node_id,
            asset_id=asset_id,
            asset_name=asset_name,
            asset_type=asset_type,
            risk_weight=risk_weight,
        )
        self._nodes[node_id] = node
        return node

    def add_edge(self, source_node_id: str, target_node_id: str, relationship_type: str = "DEPENDS_ON", propagation_factor: float = 0.5) -> AttackEdge:
        edge = AttackEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            propagation_factor=propagation_factor,
        )
        self._edges.append(edge)
        return edge

    def get_reachable_nodes(self, entry_node_id: str) -> List[str]:
        """Finds all downstream nodes reachable from entry node (analytical traversal only)."""
        visited: Set[str] = set()
        queue = [entry_node_id]

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            for edge in self._edges:
                if edge.source_node_id == curr and edge.target_node_id not in visited:
                    queue.append(edge.target_node_id)

        visited.discard(entry_node_id)
        return list(visited)
