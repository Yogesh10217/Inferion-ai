"""Unified Trust Assessment Contract (Phase 5.30)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TrustBand(str, Enum):
    HIGH_TRUST = "HIGH_TRUST"  # 90-100
    TRUSTED = "TRUSTED"        # 70-89
    RESTRICTED = "RESTRICTED"  # 50-69
    UNTRUSTED = "UNTRUSTED"    # <50


class TrustConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class TrustDimension(BaseModel):
    dimension_name: str
    score: float
    weight: float = 1.0


class TrustEvidence(BaseModel):
    evidence_id: str
    description: str


class TrustAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"trust_{uuid.uuid4().hex[:12]}")
    subject_type: str
    subject_id: str
    tenant_id: str
    score: float
    band: TrustBand
    confidence: TrustConfidence = TrustConfidence.HIGH
    dimensions: List[TrustDimension] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    version: str = "1.0.0"


class TrustAssessmentVersion(BaseModel):
    version: str = "1.0.0"
