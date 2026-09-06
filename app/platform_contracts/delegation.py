"""Delegation-Only Execution Contract (Phase 5.30)."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class DelegationTarget(str, Enum):
    PLATFORM_OPERATIONS = "PLATFORM_OPERATIONS"
    APPLICATION_PLATFORM = "APPLICATION_PLATFORM"
    DEVELOPER_PLATFORM = "DEVELOPER_PLATFORM"
    ORCHESTRATION = "ORCHESTRATION"
    INTEGRATION = "INTEGRATION"
    ARCHITECTURE_PLATFORM = "ARCHITECTURE_PLATFORM"
    PORTFOLIO_PLATFORM = "PORTFOLIO_PLATFORM"


class DelegationStatus(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    COMPENSATED = "COMPENSATED"


class DelegationRequest(BaseModel):
    delegation_id: str = Field(default_factory=lambda: f"delreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target: DelegationTarget
    action: str
    status: DelegationStatus = DelegationStatus.CREATED
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def request_id(self) -> str:
        return self.delegation_id


class DelegationResult(BaseModel):
    delegation_id: str
    status: DelegationStatus
    target_reference_id: str
    output: Dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DelegationReference(BaseModel):
    delegation_id: str
    tenant_id: str
    target: DelegationTarget
    status: DelegationStatus
