"""Cross-Phase Dependency Graph with DFS Cycle Detection and Impact Resolution."""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class CrossPhaseDependencyGraph:
    """Directed dependency graph representing cross-platform intelligence relationships."""

    def __init__(self) -> None:
        self.adj: Dict[str, Set[str]] = {}
        self._init_default_dependencies()

    def _init_default_dependencies(self) -> None:
        """Sets up the canonical cross-platform dependency relationships."""
        # Runtime -> Capacity -> Reliability -> Continuous Assurance -> Autonomous Assurance -> Decision -> Unified
        self.add_dependency("RUNTIME", "CAPACITY")
        self.add_dependency("CAPACITY", "RELIABILITY")
        self.add_dependency("RELIABILITY", "CONTINUOUS_ASSURANCE")
        self.add_dependency("CONTINUOUS_ASSURANCE", "AUTONOMOUS_ASSURANCE")
        self.add_dependency("AUTONOMOUS_ASSURANCE", "DECISION_INTELLIGENCE")
        self.add_dependency("DECISION_INTELLIGENCE", "UNIFIED_INTELLIGENCE")
        self.add_dependency("SECURITY", "CONTINUOUS_ASSURANCE")
        self.add_dependency("OPERATIONS", "RELIABILITY")

    def add_dependency(self, source: str, target: str) -> None:
        """Adds a directed edge: source depends on target."""
        u = source.upper()
        v = target.upper()
        if u not in self.adj:
            self.adj[u] = set()
        self.adj[u].add(v)
        if v not in self.adj:
            self.adj[v] = set()

    def get_dependencies(self, node: str) -> List[str]:
        """Returns direct dependencies that node relies on."""
        return sorted(list(self.adj.get(node.upper(), set())))

    def get_dependents(self, node: str) -> List[str]:
        """Returns platforms that directly depend on node."""
        target = node.upper()
        return sorted([u for u, targets in self.adj.items() if target in targets])

    def detect_cycles(self) -> List[List[str]]:
        """Detects cycles using depth-first search recursion stack."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        cycles: List[List[str]] = []

        def dfs(curr: str):
            visited.add(curr)
            rec_stack.add(curr)
            path.append(curr)

            for neighbor in self.adj.get(curr, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:] + [neighbor])

            path.pop()
            rec_stack.remove(curr)

        for n in list(self.adj.keys()):
            if n not in visited:
                dfs(n)

        return cycles

    def traverse_impact_path(self, root_node: str, max_depth: int = 5) -> List[str]:
        """Traverses downstream dependents impacted by a failure or anomaly at root_node."""
        visited: Set[str] = set()
        queue = [(root_node.upper(), 0)]
        order: List[str] = []

        while queue:
            curr, depth = queue.pop(0)
            if curr not in visited:
                visited.add(curr)
                order.append(curr)
                if depth < max_depth:
                    for dep in self.get_dependents(curr):
                        if dep not in visited:
                            queue.append((dep, depth + 1))

        return order

    def resolve_relevant_platforms(self, root_node: str) -> List[str]:
        """Discovers both direct dependencies and downstream dependents for dynamic investigation."""
        relevant = set([root_node.upper()])
        # Downstream impact
        for node in self.traverse_impact_path(root_node):
            relevant.add(node)
        # Upstream requirements
        for dep in self.get_dependencies(root_node):
            relevant.add(dep)
        return sorted(list(relevant))
