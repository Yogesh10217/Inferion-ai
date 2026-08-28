"""Enterprise Assurance Scoring Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException


class AssuranceDimension(str, Enum):
    SECURITY = "SECURITY"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    AI_SAFETY = "AI_SAFETY"
    RELIABILITY = "RELIABILITY"
    RESILIENCE = "RESILIENCE"
    COMPLIANCE = "COMPLIANCE"


class AssuranceBand(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH_RISK = "HIGH_RISK"
    ELEVATED = "ELEVATED"
    MODERATE = "MODERATE"
    STRONG = "STRONG"


class AssuranceFinding(BaseModel):
    control_id: str
    dimension: AssuranceDimension
    is_hard_failure: bool = False
    message: str


class AssuranceScore(BaseModel):
    score: float = 100.0
    band: AssuranceBand = AssuranceBand.STRONG
    hard_failures_count: int = 0


class AssuranceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"ass_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    scope_target_id: str
    assurance_score: AssuranceScore
    findings: List[AssuranceFinding] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssuranceManager:
    """Calculates enterprise assurance scores with hard failure overrides."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._assessments: Dict[str, AssuranceAssessment] = {}

    def calculate_assurance(
        self,
        tenant_id: str,
        scope_target_id: str,
        findings: Optional[List[AssuranceFinding]] = None,
    ) -> AssuranceAssessment:
        finding_list = findings or []
        hard_failures = [f for f in finding_list if f.is_hard_failure]

        if hard_failures:
            score = 35.0
            band = AssuranceBand.CRITICAL
        elif len(finding_list) > 0:
            score = 75.0
            band = AssuranceBand.MODERATE
        else:
            score = 98.0
            band = AssuranceBand.STRONG

        ass_score = AssuranceScore(
            score=score,
            band=band,
            hard_failures_count=len(hard_failures),
        )

        assessment = AssuranceAssessment(
            tenant_id=tenant_id,
            scope_target_id=scope_target_id,
            assurance_score=ass_score,
            findings=finding_list,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
