"""Knowledge Action Delegation Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.delegation import (
    DelegationRequest,
    DelegationTarget,
    DelegationStatus,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeDelegationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"kdelact_{uuid.uuid4().hex[:8]}")
    target_subsystem: DelegationTarget = DelegationTarget.ORCHESTRATION
    action_type: str = "EXECUTE_KNOWLEDGE_ACTION"
    parameters: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeDelegationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"kdelplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    delegation_request: DelegationRequest
    status: DelegationStatus = DelegationStatus.CREATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeDelegationManager:
    """Manages delegated knowledge action plans preventing direct external system mutations."""

    def delegate_action(
        self,
        tenant_id: str,
        target_id: str,
        target_subsystem: DelegationTarget = DelegationTarget.ORCHESTRATION,
        action_type: str = "EXECUTE_KNOWLEDGE_ACTION",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeDelegationPlan:
        sanitized_params = SensitiveDataSanitizer.sanitize(parameters or {})
        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=target_subsystem,
            action=action_type,
            payload=sanitized_params if isinstance(sanitized_params, dict) else {},
        )
        plan = KnowledgeDelegationPlan(
            tenant_id=tenant_id,
            target_id=target_id,
            delegation_request=del_req,
            status=DelegationStatus.CREATED,
        )
        return plan
