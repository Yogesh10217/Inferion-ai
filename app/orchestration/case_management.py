"""Long-Running Enterprise Case Management Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.orchestration.exceptions import CaseNotFoundException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CaseType(str, Enum):
    CUSTOMER_ONBOARDING = "CUSTOMER_ONBOARDING"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    FRAUD_INVESTIGATION = "FRAUD_INVESTIGATION"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    DATA_ACCESS_REQUEST = "DATA_ACCESS_REQUEST"
    DOCUMENT_PROCESSING = "DOCUMENT_PROCESSING"
    CLAIMS_PROCESSING = "CLAIMS_PROCESSING"
    EXCEPTION_HANDLING = "EXCEPTION_HANDLING"


class CaseStatus(str, Enum):
    NEW = "NEW"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    PENDING_HUMAN_TASK = "PENDING_HUMAN_TASK"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"cev_{uuid.uuid4().hex[:10]}")
    case_id: str
    event_type: str
    description: str
    timestamp: datetime = Field(default_factory=_now)


class Case(BaseModel):
    case_id: str = Field(default_factory=lambda: f"case_{uuid.uuid4().hex[:10]}")
    title: str
    case_type: CaseType = CaseType.CUSTOMER_ONBOARDING
    tenant_id: str = "global"

    status: CaseStatus = CaseStatus.NEW
    priority: CasePriority = CasePriority.MEDIUM

    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeline: List[CaseEvent] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    resolved_at: Optional[datetime] = None


class CaseManager:
    """Manages long-running enterprise case lifecycles, dynamic task creation, and timeline events."""

    def __init__(self) -> None:
        self._cases: Dict[str, Case] = {}

    def create_case(
        self,
        title: str,
        case_type: CaseType = CaseType.CUSTOMER_ONBOARDING,
        tenant_id: str = "global",
        priority: CasePriority = CasePriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Case:
        case = Case(
            title=title,
            case_type=case_type,
            tenant_id=tenant_id,
            priority=priority,
            metadata=metadata or {},
        )
        self._cases[case.case_id] = case
        self.add_timeline_event(case.case_id, "CASE_CREATED", f"Case '{title}' created")
        logger.info(
            f"[CASE MANAGER] Created case '{case.case_id}' ('{title}', {case_type.value}) for tenant '{tenant_id}'"
        )
        return case

    def update_status(self, case_id: str, new_status: CaseStatus, reason: str = "") -> Case:
        case = self.get_case(case_id)
        case.status = new_status
        case.updated_at = _now()
        if new_status in (CaseStatus.RESOLVED, CaseStatus.CLOSED):
            case.resolved_at = _now()

        self.add_timeline_event(
            case_id, f"STATUS_UPDATED_{new_status.value}", reason or f"Status updated to {new_status.value}"
        )
        logger.info(f"[CASE MANAGER] Case '{case_id}' status updated -> {new_status.value}")
        return case

    def add_timeline_event(self, case_id: str, event_type: str, description: str) -> CaseEvent:
        case = self.get_case(case_id)
        evt = CaseEvent(case_id=case_id, event_type=event_type, description=description)
        case.timeline.append(evt)
        return evt

    def get_case(self, case_id: str) -> Case:
        case = self._cases.get(case_id)
        if not case:
            raise CaseNotFoundException(case_id)
        return case

    def list_cases(self, tenant_id: Optional[str] = None) -> List[Case]:
        res = list(self._cases.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
