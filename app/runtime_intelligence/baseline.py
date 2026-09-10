"""Baseline manager for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Dict, Any, Optional
from app.runtime_intelligence.models import RuntimeBaseline

logger = logging.getLogger(__name__)


class BaselineManager:
    """Manages historical baselines and expected confidence bands.

    Invariant: Learning and baseline updates remain advisory only without auto-threshold mutation.
    """

    def __init__(self) -> None:
        self._baselines: Dict[str, RuntimeBaseline] = {}

    def get_or_create_baseline(
        self, tenant_id: str, metric_name: str, default_mean: float = 100.0, default_std: float = 15.0
    ) -> RuntimeBaseline:
        key = f"{tenant_id}:{metric_name}"
        if key not in self._baselines:
            base = RuntimeBaseline(
                tenant_id=tenant_id,
                metric_name=metric_name,
                expected_mean=default_mean,
                std_dev=default_std,
                confidence_band_lower=default_mean - (2 * default_std),
                confidence_band_upper=default_mean + (2 * default_std),
            )
            self._baselines[key] = base
            logger.info(f"Created advisory RuntimeBaseline for metric '{metric_name}' (tenant: '{tenant_id}')")
        return self._baselines[key]

    def is_within_baseline(self, tenant_id: str, metric_name: str, value: float) -> bool:
        base = self.get_or_create_baseline(tenant_id, metric_name)
        return base.confidence_band_lower <= value <= base.confidence_band_upper
