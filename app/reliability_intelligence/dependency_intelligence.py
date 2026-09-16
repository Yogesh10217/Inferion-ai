"""Dependency intelligence engine for Reliability Intelligence (Phase 5.55)."""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class ReliabilityDependencyGraph:
    """Manages service dependency graph, cycle detection, SPOF detection, and critical path analysis."""

    def __init__(self) -> None:
        self._adj: Dict[str, Set[str]] = {}

    def add_dependency(self, service: str, depends_on: str) -> None:
        if service not in self._adj:
            self._adj[service] = set()
        self._adj[service].add(depends_on)

    def detect_cycles(self) -> List[List[str]]:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        cycles: List[List[str]] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self._adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            rec_stack.remove(node)

        for node in list(self._adj.keys()):
            if node not in visited:
                dfs(node)

        return cycles

    def find_single_points_of_failure(self) -> List[str]:
        # Count incoming dependency references across services
        incoming_counts: Dict[str, int] = {}
        for deps in self._adj.values():
            for target in deps:
                incoming_counts[target] = incoming_counts.get(target, 0) + 1

        # Any node depended on by multiple services with high fan-in
        spofs = [node for node, count in incoming_counts.items() if count >= 2]
        return spofs
