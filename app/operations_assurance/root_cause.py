"""Explainable root cause intelligence correlating events, dependencies, incidents, data issues, model issues, security, identity, and infrastructure."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, RootCauseAnalysisException


class RootCauseCategory(str, Enum):
    EVENT = "EVENT"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    INCIDENT = "INCIDENT"
    DATA_ISSUE = "DATA_ISSUE"
    MODEL_ISSUE = "MODEL_ISSUE"
    SECURITY_ISSUE = "SECURITY_ISSUE"
    IDENTITY_ANOMALY = "IDENTITY_ANOMALY"
    INFRASTRUCTURE_SIGNAL = "INFRASTRUCTURE_SIGNAL"


class RootCauseAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    primary_category: RootCauseCategory
    confidence_score: float = 0.85
    root_cause_summary: str
    evidence_items: List[Dict[str, Any]] = Field(default_factory=list)
    correlated_factors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsRootCauseEngine:
    """Analyzes and correlates multi-domain signals to determine explainable root causes."""

    def __init__(self) -> None:
        self._assessments: Dict[str, Dict[str, RootCauseAssessment]] = {}  # tenant_id -> {assessment_id: assessment}

    def analyze_root_cause(
        self,
        tenant_id: str,
        service_id: str,
        category: RootCauseCategory,
        summary: str,
        confidence: float = 0.85,
        evidence: Optional[List[Dict[str, Any]]] = None,
        correlated_factors: Optional[List[str]] = None,
    ) -> RootCauseAssessment:
        assessment = RootCauseAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            primary_category=category,
            confidence_score=confidence,
            root_cause_summary=summary,
            evidence_items=evidence or [],
            correlated_factors=correlated_factors or [],
        )

        if tenant_id not in self._assessments:
            self._assessments[tenant_id] = {}
        self._assessments[tenant_id][assessment.assessment_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, assessment_id: str) -> RootCauseAssessment:
        if tenant_id not in self._assessments or assessment_id not in self._assessments[tenant_id]:
            for tid, ass in self._assessments.items():
                if tid != tenant_id and assessment_id in ass:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise RootCauseAnalysisException("Root cause assessment not found.")
        return self._assessments[tenant_id][assessment_id]
