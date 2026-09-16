"""Unified Risk Reference Contract (Phase 5.30)."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.governance_platform.risk import RiskLevel


class RiskEvidenceReference(BaseModel):
    evidence_id: str
    description: str


class RiskAssessmentReference(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"riskref_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    subject_type: str
    subject_id: str
    risk_score: float
    risk_level: RiskLevel = RiskLevel.LOW
    evidence_references: List[RiskEvidenceReference] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RiskReference(BaseModel):
    reference: RiskAssessmentReference
