"""Operational reliability intelligence evaluating MTBF, MTTR, availability, dependency resilience, and operational stability."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, ReliabilityAssessmentException


class ReliabilityScoreGrade(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MODERATE = "MODERATE"
    POOR = "POOR"
    CRITICAL = "CRITICAL"


class ReliabilityAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    reliability_score: float = 0.95
    grade: ReliabilityScoreGrade = ReliabilityScoreGrade.EXCELLENT
    availability_score: float = 0.999
    mtbf_hours: float = 720.0
    mttr_minutes: float = 15.0
    failure_frequency_30d: int = 1
    dependency_resilience_score: float = 0.9
    stability_index: float = 0.95
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsReliabilityEngine:
    """Evaluates enterprise operational reliability metrics and stability."""

    def __init__(self) -> None:
        self._assessments: Dict[str, Dict[str, ReliabilityAssessment]] = {}  # tenant_id -> {service_id: assessment}

    def assess_reliability(
        self,
        tenant_id: str,
        service_id: str,
        availability: float = 0.999,
        mtbf_hours: float = 720.0,
        mttr_minutes: float = 15.0,
        failures_30d: int = 1,
        dependency_resilience: float = 0.9,
    ) -> ReliabilityAssessment:
        # Calculate composite score
        avail_weight = 0.35
        mtbf_norm = min(1.0, mtbf_hours / 720.0)
        mttr_norm = max(0.0, 1.0 - (mttr_minutes / 120.0))
        fail_norm = max(0.0, 1.0 - (failures_30d / 10.0))

        composite = (
            availability * avail_weight
            + mtbf_norm * 0.25
            + mttr_norm * 0.20
            + fail_norm * 0.10
            + dependency_resilience * 0.10
        )

        if composite >= 0.9:
            grade = ReliabilityScoreGrade.EXCELLENT
        elif composite >= 0.8:
            grade = ReliabilityScoreGrade.GOOD
        elif composite >= 0.7:
            grade = ReliabilityScoreGrade.MODERATE
        elif composite >= 0.5:
            grade = ReliabilityScoreGrade.POOR
        else:
            grade = ReliabilityScoreGrade.CRITICAL

        assessment = ReliabilityAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            reliability_score=round(composite, 4),
            grade=grade,
            availability_score=availability,
            mtbf_hours=mtbf_hours,
            mttr_minutes=mttr_minutes,
            failure_frequency_30d=failures_30d,
            dependency_resilience_score=dependency_resilience,
            stability_index=round((mtbf_norm + mttr_norm) / 2.0, 4),
        )

        if tenant_id not in self._assessments:
            self._assessments[tenant_id] = {}
        self._assessments[tenant_id][service_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, service_id: str) -> ReliabilityAssessment:
        if tenant_id not in self._assessments or service_id not in self._assessments[tenant_id]:
            for tid, services in self._assessments.items():
                if tid != tenant_id and service_id in services:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise ReliabilityAssessmentException("Reliability assessment not found.")
        return self._assessments[tenant_id][service_id]
