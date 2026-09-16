"""Problem Management (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
)


class ProblemStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    ROOT_CAUSE_IDENTIFIED = "ROOT_CAUSE_IDENTIFIED"
    WORKAROUND_AVAILABLE = "WORKAROUND_AVAILABLE"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class OperationalProblem(BaseModel):
    problem_id: str = Field(default_factory=lambda: f"prob_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    associated_incident_ids: List[str] = Field(default_factory=list)
    status: ProblemStatus = ProblemStatus.OPEN
    workaround_details: Optional[str] = None
    root_cause_analysis_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


class ProblemManager:
    """Manages operational problem tracking lifecycle."""

    def __init__(self) -> None:
        self._problems: Dict[str, OperationalProblem] = {}

    def create_problem(
        self,
        tenant_id: str,
        title: str,
        associated_incident_ids: Optional[List[str]] = None,
    ) -> OperationalProblem:
        prob = OperationalProblem(
            tenant_id=tenant_id,
            title=title,
            associated_incident_ids=associated_incident_ids or [],
        )
        self._problems[prob.problem_id] = prob
        return prob

    def set_root_cause(self, tenant_id: str, problem_id: str, root_cause_analysis_id: str) -> OperationalProblem:
        prob = self.get_problem(tenant_id, problem_id)
        prob.root_cause_analysis_id = root_cause_analysis_id
        prob.status = ProblemStatus.ROOT_CAUSE_IDENTIFIED
        return prob

    def set_workaround(self, tenant_id: str, problem_id: str, workaround_details: str) -> OperationalProblem:
        prob = self.get_problem(tenant_id, problem_id)
        prob.workaround_details = workaround_details
        prob.status = ProblemStatus.WORKAROUND_AVAILABLE
        return prob

    def resolve_problem(self, tenant_id: str, problem_id: str) -> OperationalProblem:
        prob = self.get_problem(tenant_id, problem_id)
        prob.status = ProblemStatus.RESOLVED
        prob.resolved_at = datetime.now(timezone.utc)
        return prob

    def get_problem(self, tenant_id: str, problem_id: str) -> OperationalProblem:
        prob = self._problems.get(problem_id)
        if not prob or prob.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return prob
