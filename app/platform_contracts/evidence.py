"""Unified Evidence Reference Contract (Phase 5.30)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EvidenceStrength(str, Enum):
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    CONCLUSIVE = "CONCLUSIVE"


class EvidenceIntegrity(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    AUDITED = "AUDITED"


class EvidenceSourceReference(BaseModel):
    source_subsystem: str
    source_entity_id: str


class EvidenceMetadata(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source: EvidenceSourceReference
    strength: EvidenceStrength = EvidenceStrength.STRONG
    integrity: EvidenceIntegrity = EvidenceIntegrity.VERIFIED
    fingerprint: Optional[str] = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class EvidenceReference(BaseModel):
    metadata: EvidenceMetadata
    description: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
