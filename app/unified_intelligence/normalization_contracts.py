"""Cross-Domain Input Ingestion & Normalization Contracts."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain


class UnifiedDomainInput(BaseModel):
    """Universal contract that every domain finding/anomaly/incident converts into before entering Unified Intelligence."""

    domain: IntelligenceDomain
    tenant_id: str
    entity_reference: str
    signal_type: str
    severity: str = "MEDIUM"  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.9  # 0.0 to 1.0
    confidence_score: Optional[float] = None
    risk_score: float = 0.0  # 0.0 to 100.0
    evidence_references: List[str] = Field(default_factory=list)
    snapshot_reference: Optional[str] = None
    sanitized: bool = True
    idempotency_key: Optional[str] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def effective_confidence(self) -> float:
        if self.confidence_score is not None:
            return self.confidence_score
        return self.confidence


class NormalizedSignal(BaseModel):
    """Internal standardized signal structure created after sanitization and contract validation."""

    signal_id: str = Field(default_factory=lambda: f"norm-sig-{uuid.uuid4().hex[:8]}")
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:8]}")
    domain: IntelligenceDomain
    tenant_id: str
    entity_reference: str
    signal_type: str
    severity: str
    confidence_score: float
    risk_score: float
    evidence_ids: List[str] = Field(default_factory=list)
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    normalized_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
