"""Defensive Attack Path Finder."""

from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.security_assurance.attack_graph import AnalyticalAttackGraph


class DefensiveAttackPath(BaseModel):
    path_id: str
    tenant_id: str
    entry_asset_id: str
    target_asset_id: str
    node_sequence: List[str]
    risk_score: float
    description: str


class AttackPathFinder:
    """Finds exposure propagation paths through defensive graph analysis."""

    def __init__(self, attack_graph: AnalyticalAttackGraph) -> None:
        self.attack_graph = attack_graph

    def find_paths(self, tenant_id: str, entry_node_id: str) -> List[DefensiveAttackPath]:
        reachable = self.attack_graph.get_reachable_nodes(entry_node_id)
        paths = []
        for idx, r_id in enumerate(reachable):
            path = DefensiveAttackPath(
                path_id=f"path-{entry_node_id}-{r_id}",
                tenant_id=tenant_id,
                entry_asset_id=entry_node_id,
                target_asset_id=r_id,
                node_sequence=[entry_node_id, r_id],
                risk_score=7.5,
                description=f"Potential exposure path from {entry_node_id} to high-value asset {r_id}.",
            )
            paths.append(path)
        return paths
