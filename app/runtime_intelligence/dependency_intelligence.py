"""Runtime dependency graph intelligence for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class RuntimeDependencyGraph:
    """Models runtime component dependencies and detects cycles."""

    def __init__(self) -> None:
        self.adj: Dict[str, Set[str]] = {}

    def add_dependency(self, source: str, target: str) -> None:
        if source not in self.adj:
            self.adj[source] = set()
        self.adj[source].add(target)

    def detect_cycles(self) -> List[List[str]]:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        cycles: List[List[str]] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            rec_stack.remove(node)

        for node in list(self.adj.keys()):
            if node not in visited:
                dfs(node)

        return cycles

    def get_downstream_dependencies(self, source: str) -> List[str]:
        return list(self.adj.get(source, set()))
