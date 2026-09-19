"""Cross-Platform Correlation for Model Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CorrelationType(str, Enum):
    MODEL_INCIDENT = "MODEL_INCIDENT"
    SECURITY_INCIDENT = "SECURITY_INCIDENT"
    DATA_INCIDENT = "DATA_INCIDENT"
    OPERATIONAL_INCIDENT = "OPERATIONAL_INCIDENT"
    CONTROL_VIOLATION = "CONTROL_VIOLATION"
    ACCESS_ANOMALY = "ACCESS_ANOMALY"
    COST_ANOMALY = "COST_ANOMALY"


class CorrelationEvidence(BaseModel):
    evidence_id: str
    source_subsystem: str
    external_event_id: str
    correlation_score: float = 0.85
    details: Dict[str, Any] = Field(default_factory=dict)


class ModelCorrelation(BaseModel):
    correlation_id: str
    model_id: str
    tenant_id: str
    correlation_type: CorrelationType
    primary_event_id: str
    correlated_event_id: str
    evidence: CorrelationEvidence
    correlated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelCorrelationManager:
    """Manages cross-platform correlations across model incidents, security, data, ops, controls, access, and costs."""

    def __init__(self) -> None:
        self._correlations: Dict[str, ModelCorrelation] = {}

    def correlate_events(
        self,
        model_id: str,
        tenant_id: str,
        correlation_type: CorrelationType,
        primary_event_id: str,
        correlated_event_id: str,
        source_subsystem: str,
        correlation_score: float = 0.85,
    ) -> ModelCorrelation:
        c_id = f"mcorr-{uuid.uuid4().hex[:8]}"

        evidence = CorrelationEvidence(
            evidence_id=f"cevid-{uuid.uuid4().hex[:6]}",
            source_subsystem=source_subsystem,
            external_event_id=correlated_event_id,
            correlation_score=correlation_score,
        )

        correlation = ModelCorrelation(
            correlation_id=c_id,
            model_id=model_id,
            tenant_id=tenant_id,
            correlation_type=correlation_type,
            primary_event_id=primary_event_id,
            correlated_event_id=correlated_event_id,
            evidence=evidence,
        )

        self._correlations[c_id] = correlation
        logger.info(
            f"[MODEL CORRELATION] Correlated {primary_event_id} with {correlated_event_id} ({correlation_type})"
        )
        return correlation

    def list_correlations(self, tenant_id: str, model_id: Optional[str] = None) -> List[ModelCorrelation]:
        res = [c for c in self._correlations.values() if c.tenant_id == tenant_id]
        if model_id:
            res = [c for c in res if c.model_id == model_id]
        return res
