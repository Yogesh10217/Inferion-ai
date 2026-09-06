"""Cross-domain signal correlation intelligence for decision context synthesis."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.decision_governance.signals import DecisionSignal
from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException


class CorrelationType(str, Enum):
    INCIDENT = "INCIDENT"
    RISK = "RISK"
    COST = "COST"
    ACCESS = "ACCESS"
    CONTROL = "CONTROL"
    DATA = "DATA"
    MODEL = "MODEL"


class CorrelationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class CorrelationEvidence(BaseModel):
    signal_id_a: str
    signal_id_b: str
    correlation_reason: str
    time_delta_seconds: float = 0.0


class DecisionCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    correlation_type: CorrelationType
    title: str
    summary: str
    confidence: CorrelationConfidence = CorrelationConfidence.HIGH
    confidence_score: float = 0.88
    signals: List[DecisionSignal] = Field(default_factory=list)
    evidence: List[CorrelationEvidence] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionCorrelationManager:
    """Correlates telemetry signals across multi-domain boundaries."""

    def __init__(self) -> None:
        self._correlations: Dict[str, DecisionCorrelation] = {}

    def correlate_signals(
        self,
        tenant_id: str,
        title: str,
        signals: List[DecisionSignal],
        correlation_type: CorrelationType = CorrelationType.INCIDENT,
    ) -> DecisionCorrelation:
        evidence_list = []
        for i in range(len(signals) - 1):
            s1 = signals[i]
            s2 = signals[i + 1]
            delta = abs((s1.created_at - s2.created_at).total_seconds())
            ev = CorrelationEvidence(
                signal_id_a=s1.signal_id,
                signal_id_b=s2.signal_id,
                correlation_reason=f"Co-occurring event in {s1.source_domain.value} and {s2.source_domain.value}",
                time_delta_seconds=delta,
            )
            evidence_list.append(ev)

        summary = f"Correlated {len(signals)} signals across {len(set(s.source_domain.value for s in signals))} domains."
        corr = DecisionCorrelation(
            tenant_id=tenant_id,
            correlation_type=correlation_type,
            title=title,
            summary=summary,
            signals=signals,
            evidence=evidence_list,
        )
        self._correlations[corr.correlation_id] = corr
        return corr

    def list_correlations(self, tenant_id: str) -> List[DecisionCorrelation]:
        return [c for c in self._correlations.values() if c.tenant_id == tenant_id]
