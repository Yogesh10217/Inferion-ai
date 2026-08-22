"""Directed Resource Dependency Graph for Impact Analysis & Deletion Safety."""

import logging
from typing import Dict, Any, List, Set, Optional
from pydantic import BaseModel, Field

from app.control_plane.exceptions import ConfigurationConflictException, LifecycleException

logger = logging.getLogger(__name__)


class DependencyEdge(BaseModel):
    """Directed dependency link from parent -> child."""

    parent_id: str
    child_id: str
    dependency_type: str = "REQUIRES"  # 'REQUIRES', 'USES', 'COMPOSED_OF'


class ResourceGraph:
    """Directed acyclic dependency graph tracking resource relationships across platform subsystems."""

    def __init__(self) -> None:
        self._adj: Dict[str, Set[str]] = {}        # parent_id -> set of child_ids it depends on
        self._rev_adj: Dict[str, Set[str]] = {}    # child_id -> set of parent_ids that depend on it

    def register_dependency(self, parent_id: str, child_id: str, dependency_type: str = "REQUIRES") -> None:
        """Register a dependency edge parent -> child."""
        if parent_id not in self._adj:
            self._adj[parent_id] = set()
        if child_id not in self._rev_adj:
            self._rev_adj[child_id] = set()

        self._adj[parent_id].add(child_id)
        if child_id not in self._adj:
            self._adj[child_id] = set()
        if parent_id not in self._rev_adj:
            self._rev_adj[parent_id] = set()
        self._rev_adj[child_id].add(parent_id)

        # Check for circular dependency
        if self.detect_circular_dependencies():
            # Rollback edge
            self._adj[parent_id].remove(child_id)
            self._rev_adj[child_id].remove(parent_id)
            raise ConfigurationConflictException(f"Circular dependency detected between '{parent_id}' and '{child_id}'")

        logger.info(f"[RESOURCE GRAPH] Registered dependency: '{parent_id}' -> '{child_id}'")

    def unregister_dependency(self, parent_id: str, child_id: str) -> None:
        """Remove a dependency edge."""
        if parent_id in self._adj:
            self._adj[parent_id].discard(child_id)
        if child_id in self._rev_adj:
            self._rev_adj[child_id].discard(parent_id)

    def get_dependencies(self, resource_id: str) -> List[str]:
        """Get direct dependencies (children) of resource_id."""
        return list(self._adj.get(resource_id, set()))

    def find_dependent_resources(self, resource_id: str) -> List[str]:
        """Find resources that depend on resource_id (reverse lookup)."""
        return list(self._rev_adj.get(resource_id, set()))

    def detect_circular_dependencies(self) -> bool:
        """Detect cycles using DFS cycle detection."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self._adj.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for n in list(self._adj.keys()):
            if n not in visited:
                if dfs(n):
                    return True
        return False

    def analyze_impact(self, resource_id: str) -> Dict[str, Any]:
        """Analyze cascade impact if resource_id is deleted or modified."""
        impacted: Set[str] = set()
        queue = [resource_id]

        while queue:
            curr = queue.pop(0)
            dependents = self._rev_adj.get(curr, set())
            for dep in dependents:
                if dep not in impacted:
                    impacted.add(dep)
                    queue.append(dep)

        return {
            "resource_id": resource_id,
            "direct_dependencies": self.get_dependencies(resource_id),
            "total_impacted_resources": len(impacted),
            "impacted_resource_ids": list(impacted),
        }

    def validate_deletion_safety(self, resource_id: str) -> bool:
        """Validate if a resource can be safely deleted without breaking dependents."""
        dependents = self.find_dependent_resources(resource_id)
        if dependents:
            raise LifecycleException(
                f"Cannot delete resource '{resource_id}'. Active dependents exist: {dependents}"
            )
        return True
