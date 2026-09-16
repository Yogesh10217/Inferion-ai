"""Runtime risk propagation engine for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Optional

from app.runtime_intelligence.dependency_intelligence import RuntimeDependencyGraph
from app.runtime_intelligence.models import RuntimeRiskPropagationPath

logger = logging.getLogger(__name__)


class RuntimeRiskPropagationEngine:
    """Analyzes how runtime issues propagate across Service -> Workflow -> Decision -> Security -> Business Impact.

    Invariant: Analytical only. Zero exploitation logic.
    """

    def __init__(self, dependency_graph: Optional[RuntimeDependencyGraph] = None) -> None:
        self.dependency_graph = dependency_graph or RuntimeDependencyGraph()

    def analyze_risk_propagation(
        self,
        tenant_id: str,
        origin_component: str,
        target_component: str,
        initial_risk: float = 0.85,
        decay_factor: float = 0.90,
    ) -> RuntimeRiskPropagationPath:
        # Build propagation chain from dependency graph if available
        downstream = self.dependency_graph.get_downstream_dependencies(origin_component)
        if target_component in downstream:
            chain = [origin_component, target_component]
        elif downstream:
            intermediate = downstream[0]
            chain = [origin_component, intermediate, target_component]
        else:
            chain = [origin_component, "workflow_engine", "decision_router", target_component]

        hops = len(chain) - 1
        propagated_risk = round(initial_risk * (decay_factor ** hops), 3)

        if propagated_risk >= 0.70:
            impact = f"CRITICAL_OPERATIONAL_IMPACT_ON_{target_component.upper()}"
        elif propagated_risk >= 0.40:
            impact = f"MODERATE_LATENCY_IMPACT_ON_{target_component.upper()}"
        else:
            impact = f"LOW_RESIDUAL_IMPACT_ON_{target_component.upper()}"

        rpath = RuntimeRiskPropagationPath(
            tenant_id=tenant_id,
            origin_component=origin_component,
            target_component=target_component,
            propagation_chain=chain,
            risk_score=propagated_risk,
            business_impact=impact,
        )
        logger.info(f"Analyzed RuntimeRiskPropagationPath '{rpath.path_id}' from '{origin_component}' to '{target_component}' (Score: {propagated_risk})")
        return rpath
