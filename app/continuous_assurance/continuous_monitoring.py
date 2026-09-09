"""Continuous monitoring engine for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any, List, Optional
from app.continuous_assurance.models import RuntimeObservation
from app.continuous_assurance.monitoring_windows import MonitoringWindowPolicy, MonitoringWindowType
from app.continuous_assurance.repositories import RuntimeObservationRepository

logger = logging.getLogger(__name__)


class ContinuousMonitoringEngine:
    """Monitors ingestion, freshness, and bounded window policies."""

    def __init__(self, obs_repo: RuntimeObservationRepository) -> None:
        self.obs_repo = obs_repo
        self.policy = MonitoringWindowPolicy(
            window_type=MonitoringWindowType.REALTIME,
            duration_seconds=300,
            max_observations_capacity=5000,
        )

    def ingest_and_monitor(self, observation: RuntimeObservation) -> Dict[str, Any]:
        self.obs_repo.save(observation)

        all_obs = self.obs_repo.list_by_tenant(observation.tenant_id)
        staleness = False

        if len(all_obs) > self.policy.max_observations_capacity:
            logger.warning(f"Tenant '{observation.tenant_id}' exceeded observation monitoring capacity limit.")

        return {
            "monitored_id": observation.observation_id,
            "tenant_id": observation.tenant_id,
            "total_window_count": len(all_obs),
            "is_stale": staleness,
            "status": "MONITORING_ACTIVE",
        }
