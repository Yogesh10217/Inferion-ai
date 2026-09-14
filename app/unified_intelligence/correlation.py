"""Cross-Domain Correlation Engine for Phase 5.51 Enterprise AI Unified Intelligence."""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.context_fusion import UnifiedContext


class CorrelationType(str, Enum):
    TEMPORAL = "TEMPORAL"
    DEPENDENCY = "DEPENDENCY"
    RISK = "RISK"
    CAUSAL = "CAUSAL"
    SEMANTIC = "SEMANTIC"
    EVENT = "EVENT"


class CrossDomainCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    correlation_type: CorrelationType = CorrelationType.RISK
    primary_domain: IntelligenceDomain = IntelligenceDomain.SECURITY
    correlated_domains: List[IntelligenceDomain] = Field(default_factory=list)
    signal_ids: List[str] = Field(default_factory=list)
    correlation_strength: float = 0.85  # 0.0 to 1.0
    composite_confidence: float = 0.90
    confidence_score: float = 0.90
    summary: str = ""
    correlated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "tenant_id": self.tenant_id,
            "correlation_type": self.correlation_type.value if hasattr(self.correlation_type, 'value') else str(self.correlation_type),
            "primary_domain": self.primary_domain.value if hasattr(self.primary_domain, 'value') else str(self.primary_domain),
            "correlated_domains": [d.value if hasattr(d, 'value') else str(d) for d in self.correlated_domains],
            "signal_ids": self.signal_ids,
            "correlation_strength": round(self.correlation_strength, 4),
            "composite_confidence": round(self.composite_confidence, 4),
            "summary": self.summary,
            "correlated_at": self.correlated_at.isoformat()
        }


# Alias for backward compatibility
CorrelationGroup = CrossDomainCorrelation


class CrossDomainCorrelationEngine:
    """Correlates cross-domain platform intelligence into cohesive CrossDomainCorrelations / CorrelationGroups."""

    def __init__(self, signal_store: Optional[Any] = None) -> None:
        self.signal_store = signal_store

    def correlate_context(self, context: UnifiedContext) -> List[CrossDomainCorrelation]:
        if not context.signals:
            return []

        domains = list({s.domain for s in context.signals})
        primary = domains[0] if domains else IntelligenceDomain.SECURITY
        avg_conf = sum(getattr(s, 'confidence_score', 0.85) for s in context.signals) / len(context.signals)

        corr = CrossDomainCorrelation(
            tenant_id=context.tenant_id,
            correlation_type=CorrelationType.RISK,
            primary_domain=primary,
            correlated_domains=domains,
            signal_ids=[s.signal_id for s in context.signals],
            correlation_strength=0.88,
            composite_confidence=avg_conf,
            confidence_score=avg_conf,
            summary=f"Correlated {len(context.signals)} signals across {len(domains)} domains."
        )
        return [corr]

    def analyze_correlations(self, tenant_id: str, correlation_type: CorrelationType = CorrelationType.RISK) -> List[CrossDomainCorrelation]:
        if self.signal_store:
            signals = self.signal_store.list_signals(tenant_id)
        else:
            signals = []
        if not signals:
            return []

        domains = list({s.domain for s in signals})
        primary = domains[0] if domains else IntelligenceDomain.SECURITY

        corr = CrossDomainCorrelation(
            tenant_id=tenant_id,
            correlation_type=correlation_type,
            primary_domain=primary,
            correlated_domains=domains,
            signal_ids=[s.signal_id for s in signals],
            correlation_strength=0.88,
            composite_confidence=0.90,
            confidence_score=0.90,
            summary=f"Correlated {len(signals)} signals across {len(domains)} domains."
        )
        return [corr]
