"""Capacity optimization engine for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import CapacityOptimization, OptimizationType

logger = logging.getLogger(__name__)


class CapacityOptimizationEngine:
    """Formulates capacity optimization intelligence.

    Mandatory Invariant: auto_execute = False strictly enforced.
    """

    def analyze_optimization(
        self, tenant_id: str, target_resource_id: str, opt_type: str = "RIGHT_SIZING"
    ) -> CapacityOptimization:
        oType = (
            OptimizationType[opt_type.upper()]
            if opt_type.upper() in OptimizationType.__members__
            else OptimizationType.RIGHT_SIZING
        )

        opt = CapacityOptimization(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            optimization_type=oType,
            recommended_action=f"Right-size instance type for resource '{target_resource_id}' to reduce over-provisioned headroom",
            estimated_cost_impact_usd=65.0,
            auto_execute=False,  # Enforce advisory invariant
        )
        logger.info(
            f"Generated CapacityOptimization '{opt.optimization_id}' for resource '{target_resource_id}' (auto_execute=False)"
        )
        return opt
