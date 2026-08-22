"""
Central Operations Center Manager
"""

import logging
from typing import Dict, Any, List, Optional
from app.operations.dashboard_models import DashboardStatus
from app.autonomy.execution_governance import ExecutionGovernanceEngine

logger = logging.getLogger(__name__)


class OperationsCenter:
    """Central platform operations center managing emergency stops and global system health."""

    def __init__(self, governance: Optional[ExecutionGovernanceEngine] = None):
        self.governance = governance or ExecutionGovernanceEngine()

    def get_dashboard_summary(self, tenant_id: str = "global") -> DashboardStatus:
        return DashboardStatus(
            active_executions=2,
            active_workers=3,
            active_agents=5,
            active_teams=2,
            pending_approvals=0,
            total_cost_usd=0.15,
            global_emergency_stop=self.governance._global_emergency_stop,
            health_status="HEALTHY",
        )

    def trigger_global_emergency_stop(self, active: bool = True) -> Dict[str, Any]:
        self.governance.set_global_emergency_stop(active)
        logger.warning(f"[OPERATIONS CENTER] Global emergency stop toggled to {active}")
        return {"status": "success", "global_emergency_stop": active}
