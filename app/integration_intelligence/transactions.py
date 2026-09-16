"""Analytical Cross-System Transaction Coordination (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class TransactionState(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    COMPENSATION_REQUIRED = "COMPENSATION_REQUIRED"
    FAILED = "FAILED"


class TransactionConsistency(str, Enum):
    EVENTUAL = "EVENTUAL"
    IMMEDIATE = "IMMEDIATE"
    SAGA_PATTERN = "SAGA_PATTERN"


class IntegrationTransaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: f"txn_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    execution_id: str
    consistency: TransactionConsistency = TransactionConsistency.SAGA_PATTERN
    state: TransactionState = TransactionState.INITIATED
    completed_steps_count: int = 0
    total_steps_count: int = 1
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TransactionCoordinator:
    """Analytical transaction status tracking without implementing distributed locks."""

    def __init__(self) -> None:
        self._transactions: Dict[str, IntegrationTransaction] = {}

    def start_transaction(
        self,
        tenant_id: str,
        execution_id: str,
        total_steps_count: int = 1,
        consistency: TransactionConsistency = TransactionConsistency.SAGA_PATTERN,
    ) -> IntegrationTransaction:
        txn = IntegrationTransaction(
            tenant_id=tenant_id,
            execution_id=execution_id,
            total_steps_count=total_steps_count,
            consistency=consistency,
            state=TransactionState.IN_PROGRESS,
        )
        self._transactions[txn.transaction_id] = txn
        return txn

    def update_transaction_state(
        self,
        tenant_id: str,
        transaction_id: str,
        state: TransactionState,
        completed_steps_count: int,
    ) -> IntegrationTransaction:
        txn = self.get_transaction(tenant_id, transaction_id)
        txn.state = state
        txn.completed_steps_count = completed_steps_count
        txn.updated_at = datetime.now(timezone.utc)
        return txn

    def get_transaction(self, tenant_id: str, transaction_id: str) -> IntegrationTransaction:
        txn = self._transactions.get(transaction_id)
        if not txn or txn.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return txn
