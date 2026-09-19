"""Cross-Phase Risk Propagation Engine with Configurable Policy (Phase 5.58)."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Set

from app.platform_integration.correlation.dependency_graph import CrossPhaseDependencyGraph
from app.platform_integration.models import RiskLevel

logger = logging.getLogger(__name__)


@dataclass
class RiskPropagationPolicy:
    """Configurable policy governing risk cascading across platforms."""

    hop_decay: float = 0.7
    max_hops: int = 4
    minimum_risk: float = 0.1
    confidence_penalty: float = 0.15


@dataclass
class PropagatedRiskNode:
    platform: str
    propagated_score: float
    hops_from_source: int
    derived_risk_level: RiskLevel
    confidence: float


class CrossPhaseRiskPropagationEngine:
    """Models risk propagation across the platform dependency graph with decay attenuation."""

    def __init__(
        self,
        dep_graph: Optional[CrossPhaseDependencyGraph] = None,
        policy: Optional[RiskPropagationPolicy] = None,
    ) -> None:
        self.dep_graph = dep_graph or CrossPhaseDependencyGraph()
        self.policy = policy or RiskPropagationPolicy()

    def propagate_risk(
        self,
        tenant_id: str,
        source_platform: str,
        initial_risk_score: float,
        initial_confidence: float = 0.95,
    ) -> List[PropagatedRiskNode]:
        """Cascades risk downstream to dependent platforms using configured decay policy."""
        results: List[PropagatedRiskNode] = []
        visited: Set[str] = set()

        # BFS queue: (platform, current_score, hops, current_confidence)
        queue = [(source_platform.upper(), initial_risk_score, 0, initial_confidence)]

        while queue:
            plat, score, hops, conf = queue.pop(0)
            if plat in visited:
                continue
            visited.add(plat)

            level = self._score_to_level(score)
            results.append(
                PropagatedRiskNode(
                    platform=plat,
                    propagated_score=round(score, 3),
                    hops_from_source=hops,
                    derived_risk_level=level,
                    confidence=round(conf, 3),
                )
            )

            if hops < self.policy.max_hops:
                # Downstream dependents are impacted
                for dep in self.dep_graph.get_dependents(plat):
                    if dep not in visited:
                        next_score = score * self.policy.hop_decay
                        next_conf = max(0.1, conf - self.policy.confidence_penalty)
                        if next_score >= self.policy.minimum_risk:
                            queue.append((dep, next_score, hops + 1, next_conf))

        return results

    def _score_to_level(self, score: float) -> RiskLevel:
        if score >= 0.8:
            return RiskLevel.CRITICAL
        if score >= 0.5:
            return RiskLevel.HIGH
        if score >= 0.25:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
