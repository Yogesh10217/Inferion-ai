"""Information Lifecycle Management & Delegation-Only Retention Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.data_governance.exceptions import RetentionPolicyViolationException


class RetentionAction(str, Enum):
    RETAIN = "RETAIN"
    ARCHIVE = "ARCHIVE"
    DELETE = "DELETE"
    ANONYMIZE = "ANONYMIZE"
    LEGAL_HOLD = "LEGAL_HOLD"
    REVIEW = "REVIEW"


class LifecycleState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    COMPENSATED = "COMPENSATED"


class RetentionRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    retention_period_days: int = 365
    action: RetentionAction = RetentionAction.ARCHIVE
    applies_to_classification: Optional[str] = None


class RetentionPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    version: str = "1.0.0"
    rules: List[RetentionRule] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LegalHold(BaseModel):
    hold_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    reason: str
    case_reference: str
    placed_by: str
    placed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


class RetentionEvaluation(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    recommended_action: RetentionAction
    is_legal_hold_active: bool = False
    policy_id: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetentionExecutionRecord(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    action: RetentionAction
    idempotency_key: str
    state: LifecycleState = LifecycleState.PENDING
    delegated_subsystem: str = "PlatformOperationsManager"
    details: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetentionManager:
    """Manages information lifecycle policies, legal holds, and delegation-only execution."""

    def __init__(self) -> None:
        self._policies: Dict[str, RetentionPolicy] = {}
        self._legal_holds: Dict[str, List[LegalHold]] = {}
        self._executions: Dict[str, RetentionExecutionRecord] = {}  # idempotency_key -> record

    def create_policy(self, tenant_id: str, name: str, rules: List[RetentionRule]) -> RetentionPolicy:
        policy = RetentionPolicy(tenant_id=tenant_id, name=name, rules=rules)
        self._policies[tenant_id] = policy
        return policy

    def place_legal_hold(self, tenant_id: str, asset_id: str, reason: str, case_reference: str, placed_by: str) -> LegalHold:
        hold = LegalHold(
            tenant_id=tenant_id,
            asset_id=asset_id,
            reason=reason,
            case_reference=case_reference,
            placed_by=placed_by,
        )
        if asset_id not in self._legal_holds:
            self._legal_holds[asset_id] = []
        self._legal_holds[asset_id].append(hold)
        return hold

    def release_legal_hold(self, hold_id: str, asset_id: str) -> None:
        holds = self._legal_holds.get(asset_id, [])
        for h in holds:
            if h.hold_id == hold_id:
                h.is_active = False

    def is_under_legal_hold(self, asset_id: str, tenant_id: str) -> bool:
        holds = self._legal_holds.get(asset_id, [])
        return any(h.is_active and h.tenant_id == tenant_id for h in holds)

    def evaluate_retention(self, tenant_id: str, asset_id: str, asset_age_days: int) -> RetentionEvaluation:
        under_hold = self.is_under_legal_hold(asset_id, tenant_id)
        if under_hold:
            return RetentionEvaluation(
                tenant_id=tenant_id,
                asset_id=asset_id,
                recommended_action=RetentionAction.LEGAL_HOLD,
                is_legal_hold_active=True,
            )

        policy = self._policies.get(tenant_id)
        if not policy:
            return RetentionEvaluation(
                tenant_id=tenant_id,
                asset_id=asset_id,
                recommended_action=RetentionAction.RETAIN,
            )

        recommended = RetentionAction.RETAIN
        for rule in policy.rules:
            if asset_age_days >= rule.retention_period_days:
                recommended = rule.action

        return RetentionEvaluation(
            tenant_id=tenant_id,
            asset_id=asset_id,
            recommended_action=recommended,
            policy_id=policy.policy_id,
        )

    def prepare_delegated_execution(
        self,
        tenant_id: str,
        asset_id: str,
        action: RetentionAction,
        idempotency_key: str,
        delegated_subsystem: str = "PlatformOperationsManager",
    ) -> RetentionExecutionRecord:
        """Enforce legal hold invariants and idempotency prior to delegating execution."""

        # 1. Idempotency Check
        if idempotency_key in self._executions:
            return self._executions[idempotency_key]

        # 2. Legal Hold Invariant
        if self.is_under_legal_hold(asset_id, tenant_id):
            raise RetentionPolicyViolationException(
                f"Retention Execution Blocked: Asset '{asset_id}' is under active Legal Hold.",
                tenant_id=tenant_id,
            )

        exec_record = RetentionExecutionRecord(
            tenant_id=tenant_id,
            asset_id=asset_id,
            action=action,
            idempotency_key=idempotency_key,
            state=LifecycleState.PENDING,
            delegated_subsystem=delegated_subsystem,
        )
        self._executions[idempotency_key] = exec_record
        return exec_record

    def update_execution_state(self, idempotency_key: str, state: LifecycleState, details: Optional[Dict[str, Any]] = None) -> RetentionExecutionRecord:
        rec = self._executions.get(idempotency_key)
        if not rec:
            raise RetentionPolicyViolationException(f"Execution record '{idempotency_key}' not found.")

        rec.state = state
        if details:
            rec.details.update(details)
        return rec
