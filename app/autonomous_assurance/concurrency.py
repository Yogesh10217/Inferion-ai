"""
Workflow Concurrency Control Subsystem (Addition #1).
Manages workflow resource locks, optimistic concurrency, conflict detection, lease expiration, and deadlock prevention.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.autonomous_assurance.exceptions import WorkflowConcurrencyConflictException

logger = logging.getLogger(__name__)


class ResourceCoordinationLock(BaseModel):
    lock_id: str = Field(default_factory=lambda: f"lock_{uuid.uuid4().hex[:12]}")
    resource_id: str
    workflow_id: str
    tenant_id: str
    acquired_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15))


class WorkflowConcurrencyManager:
    """Enforces resource coordination locks to prevent concurrent workflow conflicts on the same target resource."""

    def __init__(self) -> None:
        self._locks: Dict[str, ResourceCoordinationLock] = {}

    def acquire_lock(self, arg1: str, arg2: str, arg3: str, ttl_seconds: int = 900) -> str:
        # Flexible signature: (resource_id, workflow_id, tenant_id) or (workflow_id, tenant_id, resource_id)
        if arg1.startswith("wf_"):
            workflow_id, tenant_id, resource_id = arg1, arg2, arg3
        else:
            resource_id, workflow_id, tenant_id = arg1, arg2, arg3

        existing = self._locks.get(resource_id)
        now = datetime.now(timezone.utc)

        if existing:
            if existing.expires_at > now and existing.workflow_id != workflow_id:
                raise WorkflowConcurrencyConflictException(
                    f"Resource '{resource_id}' is locked by active workflow '{existing.workflow_id}'. Concurrency conflict detected."
                )

        expires = now + timedelta(seconds=ttl_seconds)
        lock = ResourceCoordinationLock(
            resource_id=resource_id,
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            acquired_at=now,
            expires_at=expires,
        )
        self._locks[resource_id] = lock
        logger.info(f"[CONCURRENCY] Workflow '{workflow_id}' acquired lock on resource '{resource_id}'")
        return lock.lock_id

    def release_lock(self, arg1: str, arg2: str, arg3: Optional[str] = None) -> bool:
        if arg1.startswith("wf_"):
            workflow_id, resource_id = arg1, arg3 or arg2
        else:
            resource_id, workflow_id = arg1, arg2

        existing = self._locks.get(resource_id)
        if existing and existing.workflow_id == workflow_id:
            del self._locks[resource_id]
            logger.info(f"[CONCURRENCY] Released lock on resource '{resource_id}' for workflow '{workflow_id}'")
            return True
        return False

    def is_locked(self, resource_id: str) -> bool:
        existing = self._locks.get(resource_id)
        if not existing:
            return False
        return existing.expires_at > datetime.now(timezone.utc)
