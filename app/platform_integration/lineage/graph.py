"""Unified End-to-End Lineage Graph (Phase 5.58)."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Set

from app.platform_integration.exceptions import IntelligenceLineageException

logger = logging.getLogger(__name__)


class LineageNodeType(str, Enum):
    SIGNAL = "SIGNAL"
    FINDING = "FINDING"
    ASSESSMENT = "ASSESSMENT"
    RECOMMENDATION = "RECOMMENDATION"
    GOVERNANCE = "GOVERNANCE"
    APPROVAL = "APPROVAL"
    DELEGATION = "DELEGATION"
    VERIFICATION = "VERIFICATION"
    EVIDENCE = "EVIDENCE"
    SNAPSHOT = "SNAPSHOT"


@dataclass
class LineageNode:
    node_id: str
    node_type: LineageNodeType
    tenant_id: str
    platform: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class LineageGraph:
    """Directed Acyclic Graph tracking unified intelligence provenance and delegation lineage."""

    def __init__(self) -> None:
        self.nodes: Dict[str, LineageNode] = {}
        # adjacency: parent_id -> set of child_ids
        self.edges: Dict[str, Set[str]] = {}
        # reverse adjacency: child_id -> set of parent_ids
        self.reverse_edges: Dict[str, Set[str]] = {}

    def add_node(self, node: LineageNode) -> None:
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = set()
        if node.node_id not in self.reverse_edges:
            self.reverse_edges[node.node_id] = set()

    def add_edge(self, parent_id: str, child_id: str) -> None:
        if parent_id not in self.nodes:
            raise IntelligenceLineageException(f"Parent node '{parent_id}' does not exist in LineageGraph.")
        if child_id not in self.nodes:
            raise IntelligenceLineageException(f"Child node '{child_id}' does not exist in LineageGraph.")

        # Cycle prevention check
        if self._path_exists(child_id, parent_id):
            raise IntelligenceLineageException(
                f"Adding edge {parent_id} -> {child_id} would introduce a lineage cycle."
            )

        self.edges[parent_id].add(child_id)
        self.reverse_edges[child_id].add(parent_id)

    def _path_exists(self, start_id: str, target_id: str) -> bool:
        visited: Set[str] = set()
        queue = [start_id]
        while queue:
            curr = queue.pop(0)
            if curr == target_id:
                return True
            visited.add(curr)
            for child in self.edges.get(curr, []):
                if child not in visited:
                    queue.append(child)
        return False

    def backtrace_root_causes(self, start_node_id: str) -> List[LineageNode]:
        """Traces backward to discover all root ancestor nodes (e.g. initial Signals/Findings)."""
        if start_node_id not in self.nodes:
            raise IntelligenceLineageException(f"Node '{start_node_id}' not found in LineageGraph.")

        roots: List[LineageNode] = []
        visited: Set[str] = set()
        queue = [start_node_id]

        while queue:
            curr_id = queue.pop(0)
            if curr_id in visited:
                continue
            visited.add(curr_id)

            parents = self.reverse_edges.get(curr_id, set())
            if not parents:
                roots.append(self.nodes[curr_id])
            else:
                for p in parents:
                    if p not in visited:
                        queue.append(p)

        return roots

    def trace_forward_impact(self, start_node_id: str) -> List[LineageNode]:
        """Traces forward to discover all downstream descendant consequences."""
        if start_node_id not in self.nodes:
            raise IntelligenceLineageException(f"Node '{start_node_id}' not found in LineageGraph.")

        descendants: List[LineageNode] = []
        visited: Set[str] = set()
        queue = [start_node_id]

        while queue:
            curr_id = queue.pop(0)
            if curr_id in visited:
                continue
            visited.add(curr_id)
            if curr_id != start_node_id:
                descendants.append(self.nodes[curr_id])

            for child in self.edges.get(curr_id, set()):
                if child not in visited:
                    queue.append(child)

        return descendants
