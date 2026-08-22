"""Controlled Administrative Operations with Emergency Stop & Approval Requirements."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.control_plane.exceptions import ApprovalRequiredException, PlatformOperationException
from app.approvals.approval_engine import ApprovalEngine
from app.approvals.approval_policies import RiskLevel

logger = logging.getLogger(__name__)

# High-risk operations requiring approval
HIGH_RISK_OPERATIONS = {
    "emergency_stop_activate",
    "activate_emergency_stop",
    "suspend_tenant",
    "revoke_all_credentials",
    "rollback_production_config",
}



class OperationResult(BaseModel):
    """Execution status output of an administrative operation."""

    operation_id: str = Field(default_factory=lambda: f"op_{uuid.uuid4().hex[:10]}")
    action: str
    target_id: str
    tenant_id: str
    status: str  # 'COMPLETED', 'APPROVAL_REQUIRED', 'FAILED'
    approval_id: Optional[str] = None
    executed_by: str = "admin"
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = Field(default_factory=dict)


class AdminOperationsManager:
    """Executes platform operations (emergency stops, credential rotation, worker restarts, rollbacks)."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self.emergency_stop_active: bool = False
        self._operation_history: list = []

    def execute_operation(
        self,
        action: str,
        target_id: str,
        tenant_id: str = "global",
        actor_id: str = "admin",
        approved: bool = False,
        params: Optional[Dict[str, Any]] = None,
    ) -> OperationResult:
        """Execute a controlled administrative operation."""
        params = params or {}

        # 1. High-risk check
        if action in HIGH_RISK_OPERATIONS and not approved:
            req = self.approval_engine.request_approval(
                execution_id=target_id,
                action_type=action,
                risk_level=RiskLevel.HIGH,
                requester=actor_id,
                tenant_id=tenant_id,
                payload=params,
            )
            logger.warning(f"[ADMIN OPERATIONS] Action '{action}' requires approval (Approval ID: {req.request_id})")
            raise ApprovalRequiredException(action=action, approval_id=req.request_id)

        # 2. Dispatch operational logic
        status = "COMPLETED"
        details: Dict[str, Any] = {}

        if action == "activate_emergency_stop":
            self.emergency_stop_active = True
            details["message"] = "Emergency stop activated globally"
            logger.critical("[EMERGENCY STOP] Platform emergency stop ACTIVATED")
        elif action == "deactivate_emergency_stop":
            self.emergency_stop_active = False
            details["message"] = "Emergency stop deactivated"
            logger.info("[EMERGENCY STOP] Platform emergency stop DEACTIVATED")
        elif action == "restart_workers":
            details["message"] = f"Worker pool restart triggered for target '{target_id}'"
        elif action == "pause_workflows":
            details["message"] = f"Workflows paused for target '{target_id}'"
        elif action == "stop_autonomous_executions":
            details["message"] = f"Autonomous executions halted for target '{target_id}'"
        else:
            details["message"] = f"Executed action '{action}' on target '{target_id}'"

        res = OperationResult(
            action=action,
            target_id=target_id,
            tenant_id=tenant_id,
            status=status,
            executed_by=actor_id,
            details=details,
        )
        self._operation_history.append(res)
        return res

    def list_history(self, tenant_id: Optional[str] = None) -> list:
        if tenant_id:
            return [o for o in self._operation_history if o.tenant_id in (tenant_id, "global")]
        return list(self._operation_history)
