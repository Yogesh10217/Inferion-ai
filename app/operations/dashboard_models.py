"""
Operations Dashboard Metrics Models
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class DashboardStatus(BaseModel):
    active_executions: int = 0
    active_workers: int = 0
    active_agents: int = 0
    active_teams: int = 0
    pending_approvals: int = 0
    total_cost_usd: float = 0.0
    global_emergency_stop: bool = False
    health_status: str = "HEALTHY"
