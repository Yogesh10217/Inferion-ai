"""Directed Architecture Dependency Graph & Cycle Detection Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class DependencyType(str, Enum):
    CALLS = "CALLS"
    READS = "READS"
    WRITES = "WRITES"
    PRODUCES = "PRODUCES"
    CONSUMES = "CONSUMES"
    USES = "USES"
    DEPENDS_ON = "DEPENDS_ON"
    DEPLOYS = "DEPLOYS"
    GOVERNS = "GOVERN"
    AUTHORIZES = "AUTHORIZES"
    OBSERVES = "OBSERVES"
    BILLS = "BILLS"
    ORCHESTRATES = "ORCHESTRATES"


class DependencyStrength(str, Enum):
    CRITICAL = "CRITICAL"
    STRONG = "STRONG"
    WEAK = "WEAK"
    OPTIONAL = "OPTIONAL"


class DependencyDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class ArchitectureDependency(BaseModel):
    dependency_id: str = Field(default_factory=lambda: f"dep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source_node_id: str
    target_node_id: str
    dependency_type: DependencyType = DependencyType.DEPENDS_ON
    strength: DependencyStrength = DependencyStrength.STRONG
    direction: DependencyDirection = DependencyDirection.OUTBOUND
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DependencyGraph(BaseModel):
    tenant_id: str
    dependencies: Dict[str, ArchitectureDependency] = Field(default_factory=dict)
    adjacency_out: Dict[str, List[str]] = Field(default_factory=dict)  # source -> list[target]
    adjacency_in: Dict[str, List[str]] = Field(default_factory=dict)  # target -> list[source]


class DependencyManager:
    """Manages directed dependency graph, cycle detection, and transitive dependency resolution."""

    def __init__(self) -> None:
        self._graphs: Dict[str, DependencyGraph] = {}  # tenant_id -> DependencyGraph

    def _get_or_create_graph(self, tenant_id: str) -> DependencyGraph:
        if tenant_id not in self._graphs:
            self._graphs[tenant_id] = DependencyGraph(tenant_id=tenant_id)
        return self._graphs[tenant_id]

    def add_dependency(
        self,
        tenant_id: str,
        source_node_id: str,
        target_node_id: str,
        dependency_type: DependencyType = DependencyType.DEPENDS_ON,
        strength: DependencyStrength = DependencyStrength.STRONG,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArchitectureDependency:
        graph = self._get_or_create_graph(tenant_id)

        dep = ArchitectureDependency(
            tenant_id=tenant_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            dependency_type=dependency_type,
            strength=strength,
            metadata=metadata or {},
        )

        graph.dependencies[dep.dependency_id] = dep

        if source_node_id not in graph.adjacency_out:
            graph.adjacency_out[source_node_id] = []
        graph.adjacency_out[source_node_id].append(target_node_id)

        if target_node_id not in graph.adjacency_in:
            graph.adjacency_in[target_node_id] = []
        graph.adjacency_in[target_node_id].append(source_node_id)

        return dep

    def register_dependency(
        self,
        tenant_id: str,
        source_node_id: str,
        target_node_id: str,
        dependency_type: DependencyType = DependencyType.DEPENDS_ON,
        strength: DependencyStrength = DependencyStrength.STRONG,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArchitectureDependency:
        return self.add_dependency(tenant_id, source_node_id, target_node_id, dependency_type, strength, metadata)

    def list_dependencies(self, tenant_id: str, node_id: Optional[str] = None) -> List[ArchitectureDependency]:
        graph = self._get_or_create_graph(tenant_id)
        deps = list(graph.dependencies.values())
        if node_id:
            deps = [d for d in deps if d.source_node_id == node_id or d.target_node_id == node_id]
        return deps

    def detect_cycles(self, tenant_id: str) -> List[List[str]]:
        """Detect dependency cycles using DFS while preserving legitimate graph cycles."""
        graph = self._get_or_create_graph(tenant_id)
        adj = graph.adjacency_out

        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Cycle found
                    cycle_start = path.index(neighbor)
                    cycle_path = path[cycle_start:] + [neighbor]
                    if cycle_path not in cycles:
                        cycles.append(cycle_path)

            path.pop()
            rec_stack.remove(node)

        for n in list(adj.keys()):
            if n not in visited:
                dfs(n)

        return cycles

    def get_transitive_downstream(self, tenant_id: str, node_id: str) -> Set[str]:
        """Find all nodes transitively dependent on node_id (downstream blast radius)."""
        graph = self._get_or_create_graph(tenant_id)
        adj = graph.adjacency_out

        visited: Set[str] = set()
        queue = [node_id]

        while queue:
            curr = queue.pop(0)
            for neighbor in adj.get(curr, []):
                if neighbor not in visited and neighbor != node_id:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return visited

    def get_transitive_upstream(self, tenant_id: str, node_id: str) -> Set[str]:
        """Find all nodes that node_id transitively depends on (upstream roots)."""
        graph = self._get_or_create_graph(tenant_id)
        adj_in = graph.adjacency_in

        visited: Set[str] = set()
        queue = [node_id]

        while queue:
            curr = queue.pop(0)
            for parent in adj_in.get(curr, []):
                if parent not in visited and parent != node_id:
                    visited.add(parent)
                    queue.append(parent)

        return visited

    def calculate_dependency_concentration(self, tenant_id: str) -> Dict[str, Any]:
        """Calculate in-degree/out-degree concentration metrics to locate SPOFs or bottlenecks."""
        graph = self._get_or_create_graph(tenant_id)
        in_counts = {node: len(parents) for node, parents in graph.adjacency_in.items()}
        out_counts = {node: len(children) for node, children in graph.adjacency_out.items()}

        high_in_degree = sorted(in_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        high_out_degree = sorted(out_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_dependencies": len(graph.dependencies),
            "high_in_degree_nodes": high_in_degree,  # Potential SPOF / Bottleneck
            "high_out_degree_nodes": high_out_degree,  # Complex Orchestrator / Consumer
        }
