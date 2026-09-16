"""Integration Resilience, Idempotency & Saga Compensation Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.resilience.fallback import FallbackManager
from app.resilience.retry import RetryManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntegrationExecutionStatus(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    RETRYING = "RETRYING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    CANCELLED = "CANCELLED"


class IntegrationExecutionState(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"iexec_{uuid.uuid4().hex[:10]}")
    integration_id: str
    tenant_id: str = "global"
    idempotency_key: Optional[str] = None
    status: IntegrationExecutionStatus = IntegrationExecutionStatus.CREATED
    attempts: int = 1
    created_at: datetime = Field(default_factory=_now)


class IntegrationResilienceManager:
    """Manages integration retries, circuit breaking, idempotency tracking, and Saga reverse-order compensation."""

    def __init__(
        self,
        retry_manager: Optional[RetryManager] = None,
        fallback_manager: Optional[FallbackManager] = None,
    ) -> None:
        self.retry_manager = retry_manager or RetryManager()
        self.fallback_manager = fallback_manager or FallbackManager()
        self._idempotency_ledger: Dict[str, IntegrationExecutionState] = {}

    def get_or_create_execution(self, integration_id: str, idempotency_key: Optional[str] = None, tenant_id: str = "global") -> IntegrationExecutionState:
        if idempotency_key and idempotency_key in self._idempotency_ledger:
            logger.info(f"[INTEGRATION RESILIENCE] Returning idempotent execution for key '{idempotency_key}'")
            return self._idempotency_ledger[idempotency_key]

        state = IntegrationExecutionState(integration_id=integration_id, tenant_id=tenant_id, idempotency_key=idempotency_key, status=IntegrationExecutionStatus.RUNNING)
        if idempotency_key:
            self._idempotency_ledger[idempotency_key] = state
        return state
