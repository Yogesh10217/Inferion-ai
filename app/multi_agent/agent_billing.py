"""
Multi-Agent Team Billing and Cost Attribution Tracker
"""

import logging
import threading
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TeamBillingTracker:
    """Tracks team execution time, compute usage, external API calls, and per-agent cost attribution."""

    def __init__(self):
        self._lock = threading.RLock()
        self._team_usage: Dict[str, Dict[str, Any]] = {}

    def track_run(
        self,
        team_id: str,
        tenant_id: str,
        duration_seconds: float,
        cost: float,
        agent_costs: Optional[Dict[str, float]] = None,
        tool_calls: int = 0,
        api_calls: int = 0,
    ) -> Dict[str, Any]:
        with self._lock:
            if team_id not in self._team_usage:
                self._team_usage[team_id] = {
                    "team_id": team_id,
                    "tenant_id": tenant_id,
                    "total_runs": 0,
                    "total_duration_seconds": 0.0,
                    "total_cost": 0.0,
                    "tool_calls": 0,
                    "external_api_calls": 0,
                    "agent_breakdown": {},
                }

            usage = self._team_usage[team_id]
            usage["total_runs"] += 1
            usage["total_duration_seconds"] += duration_seconds
            usage["total_cost"] += cost
            usage["tool_calls"] += tool_calls
            usage["external_api_calls"] += api_calls

            if agent_costs:
                ab = usage["agent_breakdown"]
                for aid, c in agent_costs.items():
                    ab[aid] = ab.get(aid, 0.0) + c

            logger.debug(f"[TEAM BILLING] Billed team '{team_id}' (tenant '{tenant_id}') cost=${cost:.4f}")
            return usage

    def get_team_billing_summary(self, team_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._team_usage.get(team_id, {
                "team_id": team_id,
                "tenant_id": "default_tenant",
                "total_runs": 0,
                "total_duration_seconds": 0.0,
                "total_cost": 0.0,
                "tool_calls": 0,
                "external_api_calls": 0,
                "agent_breakdown": {},
            })
