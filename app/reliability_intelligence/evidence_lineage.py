"""Evidence lineage graph for Reliability Intelligence (Phase 5.55)."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ReliabilityEvidenceLineageGraph:
    """Tracks causal lineage graph across reliability lifecycle stages."""

    def __init__(self) -> None:
        self._nodes: Dict[str, List[str]] = {}

    def add_lineage_link(self, parent_id: str, child_id: str) -> None:
        if parent_id not in self._nodes:
            self._nodes[parent_id] = []
        self._nodes[parent_id].append(child_id)

    def get_lineage(self, root_id: str) -> List[str]:
        lineage = [root_id]
        curr = root_id
        while curr in self._nodes:
            next_nodes = self._nodes[curr]
            if not next_nodes:
                break
            curr = next_nodes[0]
            lineage.append(curr)
        return lineage
