"""Decision Engine & Reproducible Decision Snapshot Persistence."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.intelligence_platform.exceptions import DecisionNotFoundException, IntelligenceException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DecisionStatus(str, Enum):
    DRAFT = "DRAFT"
    EVALUATING = "EVALUATING"
    RECOMMENDED = "RECOMMENDED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DecisionOption(BaseModel):
    option_id: str = Field(default_factory=lambda: f"opt_{uuid.uuid4().hex[:10]}")
    title: str
    action_type: str
    target_resource_id: str
    expected_cost_usd: float = 0.0
    expected_latency_ms: float = 0.0
    expected_risk: str = "LOW"
    confidence: float = 0.90
    is_selected: bool = False


class DecisionCriteria(BaseModel):
    primary_objective: str = "MINIMIZE_RISK"
    cost_budget_usd: float = 100.0
    max_allowed_latency_ms: float = 500.0
    required_trust_threshold: float = 70.0


class DecisionSnapshot(BaseModel):
    """Immutable reproducible decision snapshot for enterprise auditability."""

    snapshot_id: str = Field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:10]}")
    signal_versions: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)
    policy_version: str = "v1.0.0"
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    trust_score: float = 85.0
    optimization_constraints: Dict[str, Any] = Field(default_factory=dict)
    simulation_version: str = "v1.0.0-deterministic"
    decision_algorithm_version: str = "v5.24.0"
    timestamp: datetime = Field(default_factory=_now)


class Decision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    title: str
    status: DecisionStatus = DecisionStatus.DRAFT
    criteria: DecisionCriteria = Field(default_factory=DecisionCriteria)
    options: List[DecisionOption] = Field(default_factory=list)
    selected_option: Optional[DecisionOption] = None
    approval_request_id: Optional[str] = None
    snapshot: DecisionSnapshot = Field(default_factory=DecisionSnapshot)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class DecisionManager:
    """Manages Decision lifecycle and stores reproducible audit snapshots."""

    def __init__(self) -> None:
        self._decisions: Dict[str, Decision] = {}

    def create_decision(
        self,
        tenant_id: str,
        title: str,
        criteria: Optional[DecisionCriteria] = None,
        options: Optional[List[DecisionOption]] = None,
        snapshot: Optional[DecisionSnapshot] = None,
    ) -> Decision:
        if not tenant_id:
            raise IntelligenceException("Tenant ID is required for decision creation.")

        opts = options or []
        selected = next((o for o in opts if o.is_selected), opts[0] if opts else None)

        dec = Decision(
            tenant_id=tenant_id,
            title=title,
            criteria=criteria or DecisionCriteria(),
            options=opts,
            selected_option=selected,
            snapshot=snapshot or DecisionSnapshot(),
        )

        self._decisions[dec.decision_id] = dec
        logger.info(f"[DECISION MANAGER] Created decision '{dec.decision_id}' for tenant '{tenant_id}'")
        return dec

    def update_status(self, decision_id: str, tenant_id: str, new_status: DecisionStatus, approval_request_id: Optional[str] = None) -> Decision:
        dec = self.get_decision(decision_id, tenant_id)
        dec.status = new_status
        if approval_request_id:
            dec.approval_request_id = approval_request_id
        dec.updated_at = _now()
        logger.info(f"[DECISION MANAGER] Updated decision '{decision_id}' status to {new_status.value}")
        return dec

    def get_decision(self, decision_id: str, tenant_id: str) -> Decision:
        dec = self._decisions.get(decision_id)
        if not dec or dec.tenant_id != tenant_id:
            raise DecisionNotFoundException(decision_id)
        return dec

    def list_decisions(self, tenant_id: str, status: Optional[DecisionStatus] = None) -> List[Decision]:
        res = [d for d in self._decisions.values() if d.tenant_id == tenant_id]
        if status:
            res = [d for d in res if d.status == status]
        return res
