"""Production Readiness Assessment Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException, ResilienceResourceNotFoundException


class ReadinessDimension(str, Enum):
    RELIABILITY = "RELIABILITY"
    SECURITY = "SECURITY"
    SCALABILITY = "SCALABILITY"
    RECOVERABILITY = "RECOVERABILITY"
    OBSERVABILITY = "OBSERVABILITY"
    COMPLIANCE = "COMPLIANCE"
    CAPACITY = "CAPACITY"
    GOVERNANCE = "GOVERNANCE"


class ReadinessStatus(str, Enum):
    NOT_READY = "NOT_READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    READY = "READY"


class ReadinessRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    dimension: ReadinessDimension
    name: str
    is_mandatory: bool = True
    is_passed: bool = True
    failure_reason: Optional[str] = None


class ReadinessScore(BaseModel):
    overall_score: float = 100.0
    dimension_scores: Dict[ReadinessDimension, float] = Field(default_factory=dict)


class ReadinessAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"readiness_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    status: ReadinessStatus = ReadinessStatus.READY
    score: ReadinessScore = Field(default_factory=ReadinessScore)
    requirements: List[ReadinessRequirement] = Field(default_factory=list)
    hard_failures: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductionReadinessManager:
    """Production Readiness Assessment Manager.

    Hard requirement failures override aggregate scoring to enforce NOT_READY status.
    """

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._assessments: Dict[str, ReadinessAssessment] = {}

    def assess_readiness(
        self,
        tenant_id: str,
        service_id: str,
        requirements: Optional[List[ReadinessRequirement]] = None,
    ) -> ReadinessAssessment:
        req_list = requirements or [
            ReadinessRequirement(
                dimension=ReadinessDimension.RELIABILITY, name="SLO Defined", is_mandatory=True, is_passed=True
            ),
            ReadinessRequirement(
                dimension=ReadinessDimension.SECURITY,
                name="Vulnerability Audit Clean",
                is_mandatory=True,
                is_passed=True,
            ),
            ReadinessRequirement(
                dimension=ReadinessDimension.RECOVERABILITY,
                name="DR Backup Verified",
                is_mandatory=True,
                is_passed=True,
            ),
            ReadinessRequirement(
                dimension=ReadinessDimension.OBSERVABILITY,
                name="Prometheus Metrics Collector Active",
                is_mandatory=True,
                is_passed=True,
            ),
        ]

        hard_fails = [r.name for r in req_list if r.is_mandatory and not r.is_passed]
        passed_cnt = sum(1 for r in req_list if r.is_passed)
        tot_cnt = len(req_list)
        pct = (passed_cnt / tot_cnt * 100.0) if tot_cnt > 0 else 100.0

        status = ReadinessStatus.READY
        if hard_fails:
            # HARD FAILURE OVERRIDES AGGREGATE SCORING
            status = ReadinessStatus.NOT_READY
        elif pct < 90.0:
            status = ReadinessStatus.CONDITIONALLY_READY

        assessment = ReadinessAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            status=status,
            score=ReadinessScore(overall_score=pct),
            requirements=req_list,
            hard_failures=hard_fails,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment

    def get_assessment(self, assessment_id: str, tenant_id: str) -> ReadinessAssessment:
        ass = self._assessments.get(assessment_id)
        if not ass:
            raise ResilienceResourceNotFoundException(assessment_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, ass.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, ass.tenant_id)

        return ass
