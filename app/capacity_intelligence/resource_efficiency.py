"""Resource efficiency engine for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import ResourceEfficiencyAssessment

logger = logging.getLogger(__name__)


class ResourceEfficiencyEngine:
    """Evaluates utilization efficiency, over-provisioning, under-provisioning, idle resources, and waste."""

    def evaluate_efficiency(
        self, tenant_id: str, resource_id: str, utilization_pct: float = 20.0
    ) -> ResourceEfficiencyAssessment:
        is_over = utilization_pct < 30.0
        is_under = utilization_pct > 85.0
        eff_score = round(utilization_pct / 100.0 if not is_over else 0.40, 2)
        potential_savings = 45.0 if is_over else 0.0

        eff = ResourceEfficiencyAssessment(
            tenant_id=tenant_id,
            resource_id=resource_id,
            is_overprovisioned=is_over,
            is_underprovisioned=is_under,
            efficiency_score=eff_score,
            potential_savings_usd=potential_savings,
        )
        logger.info(f"Evaluated ResourceEfficiencyAssessment for resource '{resource_id}': Over={is_over}, Under={is_under}")
        return eff
