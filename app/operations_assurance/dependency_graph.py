"""Analytical dependency graph supporting upstream/downstream analysis, blast radius, critical path, and circular dependency detection."""

from typing import Dict, Any, List, Set, Tuple, Optional
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException


class GraphNode(BaseModel):
    id: str
    tenant_id: str
    label: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticalDependencyGraph:
    """Analytical graph engine for operations dependency analysis."""

    def __init__(self) -> None:
        self._adj_list: Dict[str, Dict[str, Set[str]]] = {}  # tenant_id -> {src: set(dst)}
        self._rev_adj_list: Dict[str, Dict[str, Set[str]]] = {}  # tenant_id -> {dst: set(src)}

    def add_edge(self, tenant_id: str, source_id: str, target_id: str) -> None:
        if tenant_id not in self._adj_list:
            self._adj_list[tenant_id] = {}
            self._rev_adj_list[tenant_id] = {}

        if source_id not in self._adj_list[tenant_id]:
            self._adj_list[tenant_id][source_id] = set()
        self._adj_list[tenant_id][source_id].add(target_id)

        if target_id not in self._rev_adj_list[tenant_id]:
            self._rev_adj_list[tenant_id][target_id] = set()
        self._rev_adj_list[tenant_id][target_id].add(source_id)

    def get_upstream(self, tenant_id: str, node_id: str) -> List[str]:
        """Finds direct and indirect targets that node_id depends on."""
        tenant_adj = self._adj_list.get(tenant_id, {})
        visited: Set[str] = set()

        def dfs(curr: str) -> None:
            for neighbor in tenant_adj.get(curr, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    dfs(neighbor)

        dfs(node_id)
        return list(visited)

    def get_downstream(self, tenant_id: str, node_id: str) -> List[str]:
        """Finds direct and indirect dependents that rely on node_id."""
        tenant_rev = self._rev_adj_list.get(tenant_id, {})
        visited: Set[str] = set()

        def dfs(curr: str) -> None:
            for neighbor in tenant_rev.get(curr, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    dfs(neighbor)

        dfs(node_id)
        return list(visited)

    def compute_blast_radius(self, tenant_id: str, node_id: str) -> Dict[str, Any]:
        """Computes downstream impact set and severity score."""
        downstream = self.get_downstream(tenant_id, node_id)
        impact_count = len(downstream)
        risk_level = "CRITICAL" if impact_count > 10 else ("HIGH" if impact_count > 3 else "LOW")
        return {
            "node_id": node_id,
            "downstream_affected_count": impact_count,
            "affected_nodes": downstream,
            "blast_radius_risk": risk_level,
        }

    def detect_circular_dependencies(self, tenant_id: str) -> List[List[str]]:
        """Detects circular dependency cycles in the graph."""
        tenant_adj = self._adj_list.get(tenant_id, {})
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []

        def dfs(curr: str, path: List[str]) -> None:
            visited.add(curr)
            rec_stack.add(curr)
            path.append(curr)

            for neighbor in tenant_adj.get(curr, set()):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(curr)

        all_nodes = set(tenant_adj.keys())
        for node in all_nodes:
            if node not in visited:
                dfs(node, [])

        return cycles

    def find_critical_path(self, tenant_id: str, start_node: str, end_node: str) -> List[str]:
        """Finds paths between start and end node."""
        tenant_adj = self._adj_list.get(tenant_id, {})
        paths: List[List[str]] = []

        def dfs(curr: str, path: List[str]) -> None:
            if curr == end_node:
                paths.append(path)
                return
            for neighbor in tenant_adj.get(curr, set()):
                if neighbor not in path:
                    dfs(neighbor, path + [neighbor])

        dfs(start_node, [start_node])
        return max(paths, key=len) if paths else []
