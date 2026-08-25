"""Immutable Resource Contract & Validator (Phase 5.30)."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.platform_contracts.exceptions import ImmutableMutationException


class ImmutableResourceState(str, Enum):
    MUTABLE = "MUTABLE"
    FINALIZING = "FINALIZING"
    FINALIZED = "FINALIZED"


class ImmutableResource(BaseModel):
    resource_id: str
    tenant_id: str
    version: str = "1.0.0"
    state: ImmutableResourceState = ImmutableResourceState.MUTABLE
    fingerprint: Optional[str] = None
    finalized_at: Optional[datetime] = None


class ImmutableResourceValidator:
    """Validates immutable state transitions and blocks unauthorized mutations."""

    @staticmethod
    def ensure_mutable(resource: ImmutableResource) -> None:
        if resource.state == ImmutableResourceState.FINALIZED:
            raise ImmutableMutationException(resource.resource_id)

    @staticmethod
    def finalize(resource: ImmutableResource, fingerprint: str) -> ImmutableResource:
        ImmutableResourceValidator.ensure_mutable(resource)
        resource.state = ImmutableResourceState.FINALIZED
        resource.fingerprint = fingerprint
        resource.finalized_at = datetime.now(timezone.utc)
        return resource
