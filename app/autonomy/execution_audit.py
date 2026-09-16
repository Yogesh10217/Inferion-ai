"""
Autonomous Execution Audit Logger
"""

import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuditEntry(BaseModel):
    audit_id: str
    execution_id: str
    tenant_id: str = "default_tenant"
    action_type: str  # decision, action, approval, failure, rollback, escalation
    actor_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class ExecutionAuditLogger:
    """Multi-tenant audit logger recording all autonomous decisions, actions, and approvals."""

    def __init__(self):
        self._audit_entries: List[AuditEntry] = []

    def log(
        self,
        execution_id: str,
        action_type: str,
        actor_id: str,
        tenant_id: str = "default_tenant",
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        aid = f"audit_{int(time.time() * 1000)}"
        entry = AuditEntry(
            audit_id=aid,
            execution_id=execution_id,
            tenant_id=tenant_id,
            action_type=action_type,
            actor_id=actor_id,
            details=details or {},
        )
        self._audit_entries.append(entry)
        logger.info(f"[AUDIT LOG] execution='{execution_id}' action='{action_type}' actor='{actor_id}'")
        return entry

    def get_execution_audit(self, execution_id: str) -> List[AuditEntry]:
        return [e for e in self._audit_entries if e.execution_id == execution_id]
