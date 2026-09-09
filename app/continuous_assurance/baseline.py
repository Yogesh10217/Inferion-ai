"""Versioned runtime baseline management for Continuous Assurance (Phase 5.54)."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class RuntimeBaseline:
    tenant_id: str
    baseline_id: str
    version: int
    expected_scores: Dict[str, float]
    expected_policies: Dict[str, Any]
    expected_controls: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaselineEngine:
    """Manages versioned assurance and runtime baselines for tenant comparisons."""

    def __init__(self) -> None:
        self._baselines: Dict[str, RuntimeBaseline] = {}

    def create_baseline(
        self,
        tenant_id: str,
        expected_scores: Dict[str, float],
        expected_policies: Optional[Dict[str, Any]] = None,
        expected_controls: Optional[Dict[str, Any]] = None,
    ) -> RuntimeBaseline:
        existing = [b for b in self._baselines.values() if b.tenant_id == tenant_id]
        next_ver = len(existing) + 1
        b_id = f"base_{tenant_id}_v{next_ver}"

        baseline = RuntimeBaseline(
            tenant_id=tenant_id,
            baseline_id=b_id,
            version=next_ver,
            expected_scores=expected_scores,
            expected_policies=expected_policies or {},
            expected_controls=expected_controls or {},
        )

        self._baselines[b_id] = baseline
        logger.info(f"Created versioned RuntimeBaseline '{b_id}' (v{next_ver}) for tenant '{tenant_id}'")
        return baseline

    def get_latest_baseline(self, tenant_id: str) -> Optional[RuntimeBaseline]:
        existing = [b for b in self._baselines.values() if b.tenant_id == tenant_id]
        if not existing:
            return None
        return max(existing, key=lambda b: b.version)
