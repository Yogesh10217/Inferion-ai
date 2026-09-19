"""Context Fusion Engine with Bounded Context Policies for Phase 5.51 Enterprise AI Unified Intelligence."""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain

logger = logging.getLogger(__name__)


class UnifiedContextPolicy(BaseModel):
    max_signals: int = 50
    max_age_hours: int = 24
    max_domains: int = 10
    aggregation_strategy: str = "SLIDING_WINDOW"


class UnifiedContext(BaseModel):
    context_id: str = Field(default_factory=lambda: f"unif-ctx-{uuid.uuid4().hex[:8]}")
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    domains: List[IntelligenceDomain] = Field(default_factory=list)
    signal_ids: List[str] = Field(default_factory=list)
    signals: List[Any] = Field(default_factory=list)
    context_fingerprint: str = ""
    confidence_score: float = 0.9
    unified_summary: str = ""
    fused_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def participating_domains(self) -> List[IntelligenceDomain]:
        return self.domains

    @property
    def sha256_fingerprint(self) -> str:
        return self.context_fingerprint

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "correlation_id": self.correlation_id,
            "tenant_id": self.tenant_id,
            "domains": [d.value if hasattr(d, "value") else str(d) for d in self.domains],
            "signal_ids": self.signal_ids,
            "context_fingerprint": self.context_fingerprint,
            "confidence_score": round(self.confidence_score, 4),
            "unified_summary": self.unified_summary,
            "fused_at": self.fused_at.isoformat(),
        }


class ContextFusionEngine:
    """Fuses multi-domain signals into a bounded UnifiedContext with SHA-256 fingerprinting."""

    def __init__(self, signal_store: Optional[Any] = None, policy: Optional[UnifiedContextPolicy] = None) -> None:
        self.signal_store = signal_store
        self.policy = policy or UnifiedContextPolicy()

    def fuse_context(
        self,
        tenant_id: str,
        signals: Optional[List[Any]] = None,
        policy: Optional[UnifiedContextPolicy] = None,
        target_domains: Optional[List[IntelligenceDomain]] = None,
        correlation_id: Optional[str] = None,
    ) -> UnifiedContext:
        active_policy = policy or self.policy

        if signals is None:
            if self.signal_store:
                signals = self.signal_store.list_signals(tenant_id)
            else:
                signals = []

        if target_domains:
            signals = [s for s in signals if getattr(s, "domain", None) in target_domains]

        # Apply context bounding policy (max_signals limit)
        bounded_signals = signals[-active_policy.max_signals :] if len(signals) > active_policy.max_signals else signals

        # Bounded domains
        all_domains = []
        for s in bounded_signals:
            d = getattr(s, "domain", None)
            if d and d not in all_domains:
                all_domains.append(d)
        domains = all_domains[: active_policy.max_domains]

        # Filter signals to only those in bounded domains
        final_signals = [s for s in bounded_signals if getattr(s, "domain", None) in domains]
        signal_ids = [getattr(s, "signal_id", f"sig-{i}") for i, s in enumerate(final_signals)]

        # Generate SHA-256 context fingerprint
        data = {
            "tenant_id": tenant_id,
            "signal_ids": sorted(signal_ids),
            "domains": [d.value if hasattr(d, "value") else str(d) for d in domains],
        }
        fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

        summary = f"Fused context across {len(domains)} domains with {len(final_signals)} signals."

        return UnifiedContext(
            correlation_id=correlation_id or f"corr-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            domains=domains,
            signal_ids=signal_ids,
            signals=final_signals,
            context_fingerprint=fingerprint,
            unified_summary=summary,
        )
