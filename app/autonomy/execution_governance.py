"""
Execution Governance Engine & Safety Controls
"""

import logging
from typing import Dict, List, Optional

from app.autonomy.exceptions import AutonomyException, EmergencyStopException

logger = logging.getLogger(__name__)


class ExecutionGovernanceEngine:
    """Enforces workspace budget caps, tenant boundaries, safety policies, and emergency stops."""

    def __init__(self):
        self._global_emergency_stop: bool = False
        self._tenant_emergency_stops: Dict[str, bool] = {}

    def set_global_emergency_stop(self, active: bool) -> None:
        self._global_emergency_stop = active
        logger.warning(f"[GOVERNANCE] Global emergency stop status set to {active}")

    def set_tenant_emergency_stop(self, tenant_id: str, active: bool) -> None:
        self._tenant_emergency_stops[tenant_id] = active
        logger.warning(f"[GOVERNANCE] Tenant emergency stop for '{tenant_id}' set to {active}")

    def validate_execution_start(
        self,
        tenant_id: str,
        workspace_id: str,
        cost_so_far: float,
        budget_limit: float = 100.0,
        user_scopes: Optional[List[str]] = None,
    ) -> None:
        if self._global_emergency_stop:
            raise EmergencyStopException("GLOBAL EMERGENCY STOP ACTIVATED: All autonomous executions halted")

        if self._tenant_emergency_stops.get(tenant_id, False):
            raise EmergencyStopException(f"TENANT EMERGENCY STOP ACTIVATED for tenant '{tenant_id}': Execution halted")

        user_scopes = user_scopes or ["autonomy:run"]
        if "autonomy:run" not in user_scopes and "admin" not in user_scopes:
            raise AutonomyException(f"User scopes {user_scopes} missing required scope 'autonomy:run'")

        if cost_so_far > budget_limit:
            raise AutonomyException(f"Workspace budget limit exceeded: cost ${cost_so_far:.4f} > limit ${budget_limit:.4f}")
