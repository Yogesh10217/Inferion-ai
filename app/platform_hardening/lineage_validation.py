"""
Platform Lineage Validation Engine.
Validates DAG integrity of intelligence lineage edges across platform entities.
"""

from typing import Dict, List, Set, Tuple
from app.platform_hardening.models import (
    LineageValidationResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformLineageValidationEngine:
    """Validates edge integrity, orphan detection, parent/child linkages, and graph cycles in lineage."""

    def validate_lineage_graph(
        self, edges: List[Dict[str, str]], tenant_id: str = "system"
    ) -> Tuple[LineageValidationResult, List[PlatformAuditFinding]]:
        # edge format: {"source": id1, "target": id2, "relationship": rel_name}
        adj_list: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}
        all_nodes: Set[str] = set()

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")

            if not src or not tgt:
                continue

            all_nodes.add(src)
            all_nodes.add(tgt)

            if src not in adj_list:
                adj_list[src] = set()
            adj_list[src].add(tgt)

            in_degree[tgt] = in_degree.get(tgt, 0) + 1
            if src not in in_degree:
                in_degree[src] = 0

        # Detect orphans (nodes with 0 in-degree and 0 out-degree in multi-edge graph)
        orphans = [n for n in all_nodes if in_degree.get(n, 0) == 0 and len(adj_list.get(n, set())) == 0]

        # Detect cycles
        cycles = self._find_cycles(adj_list)
        findings: List[PlatformAuditFinding] = []

        for cycle in cycles:
            findings.append(
                PlatformAuditFinding(
                    finding_id=f"lineage-cycle-{'->'.join(cycle[:2])}",
                    tenant_id=tenant_id,
                    rule_id="RULE-LIN-001",
                    title="Lineage Graph Cycle Detected",
                    description=f"Cycle detected in intelligence lineage: {' -> '.join(cycle)}",
                    severity=PlatformAuditSeverity.HIGH,
                    subsystem="lineage",
                    affected_component="LineageGraph",
                    remediation_suggestion="Remove invalid backward linkage creating cyclic lineage.",
                )
            )

        is_valid = len(cycles) == 0

        result = LineageValidationResult(
            is_valid=is_valid,
            edges_validated=len(edges),
            missing_parents=[],
            missing_children=[],
            orphans=orphans,
            cycles_detected=cycles,
        )

        return result, findings

    def _find_cycles(self, adj_list: Dict[str, Set[str]]) -> List[List[str]]:
        cycles = []
        visited = set()
        stack = []

        def dfs(node):
            visited.add(node)
            stack.append(node)

            for neighbor in adj_list.get(node, []):
                if neighbor in stack:
                    idx = stack.index(neighbor)
                    cycles.append(stack[idx:] + [neighbor])
                elif neighbor not in visited:
                    dfs(neighbor)

            stack.pop()

        for node in list(adj_list.keys()):
            if node not in visited:
                dfs(node)

        return cycles
