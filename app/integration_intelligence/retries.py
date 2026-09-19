"""Governed Retry Intelligence & Dead-Letter Handling (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import IntegrationRetryException


class RetryStatus(str, Enum):
    ALLOWED = "ALLOWED"
    EXCEEDED_SENT_TO_DEAD_LETTER = "EXCEEDED_SENT_TO_DEAD_LETTER"
    BACKOFF_WAIT = "BACKOFF_WAIT"


class RetryPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"ret_pol_{uuid.uuid4().hex[:8]}")
    max_retries: int = 3
    initial_backoff_seconds: int = 5
    max_backoff_seconds: int = 300
    backoff_multiplier: float = 2.0


class RetryDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"ret_dec_{uuid.uuid4().hex[:8]}")
    execution_id: str
    status: RetryStatus
    attempt_count: int
    next_backoff_seconds: int = 0
    dead_letter_queue_id: Optional[str] = None
    reason: str = ""


class RetryManager:
    """Manages retry limits, backoff policy evaluation, and dead-letter queue routing."""

    def __init__(self) -> None:
        self._decisions: Dict[str, RetryDecision] = {}
        self._dead_letter_queue: List[Dict[str, Any]] = []

    def evaluate_retry(
        self,
        tenant_id: str,
        execution_id: str,
        attempt_count: int,
        policy: Optional[RetryPolicy] = None,
    ) -> RetryDecision:
        policy = policy or RetryPolicy()

        if attempt_count >= policy.max_retries:
            dlq_id = f"dlq_{uuid.uuid4().hex[:8]}"
            self._dead_letter_queue.append(
                {
                    "tenant_id": tenant_id,
                    "execution_id": execution_id,
                    "attempt_count": attempt_count,
                    "dead_letter_id": dlq_id,
                    "queued_at": datetime.now(timezone.utc).isoformat(),
                }
            )

            dec = RetryDecision(
                execution_id=execution_id,
                status=RetryStatus.EXCEEDED_SENT_TO_DEAD_LETTER,
                attempt_count=attempt_count,
                dead_letter_queue_id=dlq_id,
                reason=f"Retry limit ({policy.max_retries}) exceeded. Routed to dead-letter queue '{dlq_id}'.",
            )
            self._decisions[dec.decision_id] = dec
            raise IntegrationRetryException(attempt_count, policy.max_retries)

        backoff = min(
            policy.max_backoff_seconds,
            int(policy.initial_backoff_seconds * (policy.backoff_multiplier ** (attempt_count - 1))),
        )

        dec = RetryDecision(
            execution_id=execution_id,
            status=RetryStatus.ALLOWED,
            attempt_count=attempt_count,
            next_backoff_seconds=backoff,
            reason=f"Retry attempt {attempt_count}/{policy.max_retries} allowed after {backoff}s backoff.",
        )
        self._decisions[dec.decision_id] = dec
        return dec

    def list_dead_letter_entries(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [e for e in self._dead_letter_queue if e["tenant_id"] == tenant_id]
