"""Architecture Change Lifecycle & Proposal Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.architecture_platform.exceptions import (
    ArchitectureChangeNotFoundException,
    ArchitectureChangeIdempotencyException,
)


class ArchitectureChangeType(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    REMOVE = "REMOVE"
    MIGRATE = "MIGRATE"
    REPLACE = "REPLACE"
    SCALE = "SCALE"
    ROUTE = "ROUTE"
    GOVERN = "GOVERN"


class ArchitectureChangeStatus(str, Enum):
    DRAFT = "DRAFT"
    ANALYZING = "ANALYZING"
    POLICY_EVALUATION = "POLICY_EVALUATION"
    RISK_EVALUATION = "RISK_EVALUATION"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    CANCELLED = "CANCELLED"


class ArchitectureChangeProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action_type: ArchitectureChangeType
    target_node_id: str
    replacement_node_id: Optional[str] = None
    reason: str
    proposed_by: str = "system"


class ArchitectureChange(BaseModel):
    """Architecture Change Lifecycle object enforcing idempotency."""

    change_id: str = Field(default_factory=lambda: f"change_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    idempotency_key: str
    action_type: ArchitectureChangeType
    target_node_ids: List[str] = Field(default_factory=list)
    status: ArchitectureChangeStatus = ArchitectureChangeStatus.DRAFT
    requested_by: str = "system"
    risk_level: str = "MEDIUM"
    approval_request_id: Optional[str] = None
    delegated_subsystem: Optional[str] = None
    audit_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureChangeManager:
    """Manages architecture change proposals, idempotency, and lifecycle state transitions."""

    def __init__(self) -> None:
        self._changes: Dict[str, ArchitectureChange] = {}  # change_id -> ArchitectureChange
        self._idempotency_index: Dict[str, ArchitectureChange] = {}  # idempotency_key -> ArchitectureChange

    def propose_change(
        self,
        tenant_id: str,
        idempotency_key: str,
        action_type: ArchitectureChangeType,
        target_node_ids: List[str],
        requested_by: str = "system",
        risk_level: str = "MEDIUM",
    ) -> ArchitectureChange:
        # Idempotency check
        if idempotency_key in self._idempotency_index:
            return self._idempotency_index[idempotency_key]

        change = ArchitectureChange(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            action_type=action_type,
            target_node_ids=target_node_ids,
            status=ArchitectureChangeStatus.DRAFT,
            requested_by=requested_by,
            risk_level=risk_level,
        )

        self._changes[change.change_id] = change
        self._idempotency_index[idempotency_key] = change
        return change

    def get_change(self, change_id: str, tenant_id: str) -> ArchitectureChange:
        change = self._changes.get(change_id)
        if not change or (change.tenant_id != tenant_id and tenant_id != "system"):
            raise ArchitectureChangeNotFoundException(change_id=change_id, tenant_id=tenant_id)
        return change

    def update_status(self, change_id: str, tenant_id: str, status: ArchitectureChangeStatus) -> ArchitectureChange:
        change = self.get_change(change_id, tenant_id)
        change.status = status
        change.updated_at = datetime.now(timezone.utc)
        return change
