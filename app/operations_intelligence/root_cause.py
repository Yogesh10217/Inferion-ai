"""Root Cause Analysis Intelligence (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class RootCauseConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RootCauseEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"rca_ev_{uuid.uuid4().hex[:8]}")
    source: str
    description: str


class RootCauseHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: f"hypo_{uuid.uuid4().hex[:8]}")
    title: str
    component_name: str
    likelihood_score: float = 80.0
    reasoning: str


class RootCauseAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"rca_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    primary_root_cause: str
    confidence: RootCauseConfidence = RootCauseConfidence.HIGH
    hypotheses: List[RootCauseHypothesis] = Field(default_factory=list)
    evidence: List[RootCauseEvidence] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RootCauseManager:
    """Manages explainable root cause hypothesis generation and evidence collection."""

    def __init__(self) -> None:
        self._analyses: Dict[str, RootCauseAnalysis] = {}

    def analyze_root_cause(
        self,
        tenant_id: str,
        incident_id: str,
        primary_root_cause: str,
        hypotheses: List[RootCauseHypothesis],
        evidence: List[RootCauseEvidence],
        confidence: RootCauseConfidence = RootCauseConfidence.HIGH,
    ) -> RootCauseAnalysis:
        rca = RootCauseAnalysis(
            tenant_id=tenant_id,
            incident_id=incident_id,
            primary_root_cause=primary_root_cause,
            confidence=confidence,
            hypotheses=hypotheses,
            evidence=evidence,
        )
        self._analyses[rca.analysis_id] = rca
        return rca

    def get_analysis(self, tenant_id: str, analysis_id: str) -> RootCauseAnalysis:
        rca = self._analyses.get(analysis_id)
        if not rca or rca.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return rca
