"""Unified Risk Reference Contract (Phase 5.30)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.risk import RiskManager, RiskLevel


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
