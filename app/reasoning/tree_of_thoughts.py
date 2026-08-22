"""
Tree of Thoughts (ToT) Branching & Reasoning Search Engine
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ThoughtNode(BaseModel):
    node_id: str = Field(default_factory=lambda: f"thought_{uuid.uuid4().hex[:8]}")
    parent_id: Optional[str] = None
    thought_content: str
    score: float = 0.5
    is_pruned: bool = False
    children_ids: List[str] = Field(default_factory=list)


class TreeOfThoughtsEngine:
    """Explores alternative reasoning paths (Tree of Thoughts) with scoring and pruning."""

    def __init__(self, max_depth: int = 3, max_branches: int = 3, min_score_threshold: float = 0.4):
        self.max_depth = max_depth
        self.max_branches = max_branches
        self.min_score_threshold = min_score_threshold

    def search_best_path(self, goal_prompt: str) -> Dict[str, Any]:
        """Generate thought tree, score branches, prune low scores, and return best path."""
        nodes: Dict[str, ThoughtNode] = {}

        # Root node
        root = ThoughtNode(thought_content=f"Root analysis for: '{goal_prompt}'", score=0.9)
        nodes[root.node_id] = root

        current_level = [root.node_id]

        for depth in range(1, self.max_depth + 1):
            next_level = []
            for parent_id in current_level:
                parent = nodes[parent_id]
                if parent.is_pruned:
                    continue

                for b in range(self.max_branches):
                    score = min(0.98, max(0.2, 0.5 + (0.15 * (b + depth - 1))))
                    is_pruned = score < self.min_score_threshold
                    child = ThoughtNode(
                        parent_id=parent_id,
                        thought_content=f"Path branch {b+1} depth {depth}: evaluate strategy {chr(65+b)}",
                        score=score,
                        is_pruned=is_pruned,
                    )
                    nodes[child.node_id] = child
                    parent.children_ids.append(child.node_id)
                    if not is_pruned:
                        next_level.append(child.node_id)

            if not next_level:
                break
            current_level = next_level

        # Find best active non-root node if available
        child_active = [n for n in nodes.values() if not n.is_pruned and n.node_id != root.node_id]
        best_node = max(child_active, key=lambda x: x.score) if child_active else root

        # Reconstruct path
        path = []
        curr = best_node
        while curr:
            path.append(curr.thought_content)
            curr = nodes.get(curr.parent_id) if curr.parent_id else None
        path.reverse()

        logger.info(f"[TREE OF THOUGHTS] Selected best path with score {best_node.score:.2f} across {len(nodes)} generated nodes")
        return {
            "best_score": best_node.score,
            "best_path": path,
            "total_nodes_generated": len(nodes),
            "pruned_nodes_count": len([n for n in nodes.values() if n.is_pruned]),
        }
