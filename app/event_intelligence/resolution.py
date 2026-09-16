"""Event Resolution Lifecycle Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.event_intelligence.exceptions import (
    CrossTenantEventAccessException,
    EventResolutionException,
    ImmutableEventRecordException,
)
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator


class EventResolutionStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESPONSE_PLANNED = "RESPONSE_PLANNED"
    DELEGATED = "DELEGATED"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class ResolutionEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"revid_{uuid.uuid4().hex[:12]}")
    description: str


class ResolutionVerification(BaseModel):
    is_verified: bool = True
    verified_by: str = "SYSTEM"


class EventResolution(BaseModel):
    resolution_id: str = Field(default_factory=lambda: f"res_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    event_id: str
    status: EventResolutionStatus = EventResolutionStatus.OPEN
    evidence: List[ResolutionEvidence] = Field(default_factory=list)
    verification: Optional[ResolutionVerification] = None
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(resource_id=self.resolution_id, tenant_id=self.tenant_id)


class EventResolutionManager:
    """Manages event resolution lifecycle and produces immutable final resolution records."""

    def __init__(self) -> None:
        self._resolutions: Dict[str, EventResolution] = {}

    def create_resolution(self, tenant_id: str, event_id: str) -> EventResolution:
        res = EventResolution(tenant_id=tenant_id, event_id=event_id, status=EventResolutionStatus.OPEN)
        self._resolutions[res.resolution_id] = res
        return res

    def transition_resolution(
        self,
        resolution_id: str,
        tenant_id: str,
        target_status: EventResolutionStatus,
    ) -> EventResolution:
        res = self._resolutions.get(resolution_id)
        if not res:
            raise KeyError(f"Resolution '{resolution_id}' not found.")
        if tenant_id != "global" and res.tenant_id != "global" and tenant_id != res.tenant_id:
            raise CrossTenantEventAccessException(tenant_id, res.tenant_id)

        if res.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableEventRecordException(resolution_id)

        # Enforce valid lifecycle transitions
        valid_transitions = {
            EventResolutionStatus.OPEN: [EventResolutionStatus.INVESTIGATING, EventResolutionStatus.RESPONSE_PLANNED],
            EventResolutionStatus.INVESTIGATING: [EventResolutionStatus.RESPONSE_PLANNED, EventResolutionStatus.DELEGATED],
            EventResolutionStatus.RESPONSE_PLANNED: [EventResolutionStatus.DELEGATED],
            EventResolutionStatus.DELEGATED: [EventResolutionStatus.VERIFYING],
            EventResolutionStatus.VERIFYING: [EventResolutionStatus.RESOLVED],
            EventResolutionStatus.RESOLVED: [EventResolutionStatus.CLOSED],
            EventResolutionStatus.CLOSED: [],
        }

        allowed = valid_transitions.get(res.status, [])
        if target_status not in allowed:
            raise EventResolutionException(f"Invalid resolution transition from '{res.status.value}' to '{target_status.value}'.")

        res.status = target_status
        if target_status in (EventResolutionStatus.RESOLVED, EventResolutionStatus.CLOSED):
            res.verification = ResolutionVerification(is_verified=True)
            fp = FingerprintGenerator.generate(res.model_dump(exclude={"immutable_record"}))
            ImmutableResourceValidator.finalize(res.immutable_record, fingerprint=fp)

        return res
