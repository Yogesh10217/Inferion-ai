"""Capacity intelligence engine (Phase 5.55)."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CapacityIntelligenceEngine:
    """Analyzes utilization, headroom, saturation risk, and capacity exhaustion horizons."""

    def evaluate_capacity(self, tenant_id: str, service_id: str, utilization: float = 0.65) -> Dict[str, Any]:
        headroom = round(100.0 - (utilization * 100.0), 2)
        is_at_risk = utilization > 0.85

        return {
            "service_id": service_id,
            "tenant_id": tenant_id,
            "utilization_pct": round(utilization * 100.0, 2),
            "headroom_pct": headroom,
            "is_at_risk": is_at_risk,
            "exhaustion_horizon_days": 14 if is_at_risk else 120,
        }
