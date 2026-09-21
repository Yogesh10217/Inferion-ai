"""Runtime degradation engine for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import List, Optional

from app.runtime_intelligence.models import RuntimeDegradation

logger = logging.getLogger(__name__)


class RuntimeDegradationEngine:
    """Analyzes system degradation trajectories across service, workflow, and capacity boundaries."""

    def analyze_degradation(
        self,
        tenant_id: str,
        service_id: str,
        degradation_type: str = "PERFORMANCE",
        historical_scores: Optional[List[float]] = None,
    ) -> RuntimeDegradation:
        scores = historical_scores or [0.95, 0.90, 0.82, 0.75]

        if len(scores) >= 2:
            initial = scores[0]
            latest = scores[-1]
            delta = initial - latest
            delta / max(1, len(scores) - 1)
        else:
            delta = 0.10
            latest = scores[0] if scores else 0.85

        impact_score = round(min(1.0, max(0.0, delta * 1.5 + (1.0 - latest))), 3)

        if delta > 0.30:
            trend = "RAPIDLY_DEGRADING"
            time_to_critical = max(300.0, 1800.0 * (latest / max(0.01, delta)))
        elif delta > 0.10:
            trend = "DEGRADED"
            time_to_critical = max(1800.0, 3600.0 * (latest / max(0.01, delta)))
        else:
            trend = "STABLE_OR_RECOVERING"
            time_to_critical = 86400.0

        features = [f"{service_id}_core_api", f"{service_id}_batch_processing"]
        if impact_score > 0.50:
            features.append(f"{service_id}_analytics_sync")

        deg = RuntimeDegradation(
            tenant_id=tenant_id,
            service_id=service_id,
            degradation_type=degradation_type,
            impact_score=impact_score,
            affected_features=features,
            degradation_trend=trend,
            estimated_time_to_critical_seconds=round(time_to_critical, 1),
        )
        logger.info(f"Analyzed RuntimeDegradation '{deg.degradation_id}' for service '{service_id}' (Trend: {trend})")
        return deg
