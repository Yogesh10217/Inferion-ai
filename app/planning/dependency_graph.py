"""
DAG Dependency Engine with Cycle Detection & Critical Path Calculation
"""

from typing import Dict, List

from app.planning.exceptions import DependencyResolutionError
from app.planning.goals import Task


class DependencyGraph:
    """DAG graph solver for task dependency resolution."""

    def __init__(self, tasks: List[Task]):
        self.tasks_map: Dict[str, Task] = {t.task_id: t for t in tasks}
        self.adj_list: Dict[str, List[str]] = {t.task_id: [] for t in tasks}
        self.in_degree: Dict[str, int] = {t.task_id: 0 for t in tasks}

        for t in tasks:
            for dep_id in t.dependencies:
                if dep_id in self.tasks_map:
                    self.adj_list[dep_id].append(t.task_id)
                    self.in_degree[t.task_id] += 1

    def detect_cycle(self) -> bool:
        """Kahn's topological sort cycle check."""
        in_deg = dict(self.in_degree)
        queue = [tid for tid, deg in in_deg.items() if deg == 0]
        visited_count = 0

        while queue:
            node = queue.pop(0)
            visited_count += 1
            for neighbor in self.adj_list.get(node, []):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        return visited_count != len(self.tasks_map)

    def get_execution_order(self) -> List[str]:
        """Return topological ordering of task IDs."""
        if self.detect_cycle():
            raise DependencyResolutionError("Circular dependency detected in plan task DAG")

        in_deg = dict(self.in_degree)
        queue = [tid for tid, deg in in_deg.items() if deg == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in self.adj_list.get(node, []):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        return order

    def calculate_critical_path(self) -> List[str]:
        """Calculate longest execution duration path in DAG."""
        order = self.get_execution_order()
        dist: Dict[str, float] = {tid: 0.0 for tid in order}
        parent: Dict[str, str] = {}

        for tid in order:
            task_duration = self.tasks_map[tid].estimated_duration_seconds
            current_dist = dist[tid] + task_duration
            for neighbor in self.adj_list.get(tid, []):
                if current_dist > dist[neighbor]:
                    dist[neighbor] = current_dist
                    parent[neighbor] = tid

        if not dist:
            return []

        end_node = max(dist.items(), key=lambda x: x[1])[0]
        path = []
        curr = end_node
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(curr)
        path.reverse()
        return path
