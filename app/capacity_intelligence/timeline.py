"""Capacity timeline recorder for Capacity Intelligence (Phase 5.56)."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CapacityTimeline:
    """Chronologically records capacity telemetry, forecasts, bottlenecks, recommendations, delegations, and verification events."""

    def __init__(self) -> None:
        self._timeline: Dict[str, List[Dict[str, Any]]] = {}

    def record_event(self, tenant_id: str, event_type: str, details: str) -> Dict[str, Any]:
        if tenant_id not in self._timeline:
            self._timeline[tenant_id] = []
        event = {
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._timeline[tenant_id].append(event)
        logger.debug(f"Recorded capacity timeline event '{event_type}' for tenant '{tenant_id}'")
        return event

    def get_timeline(self, tenant_id: str) -> List[Dict[str, Any]]:
        return self._timeline.get(tenant_id, [])
