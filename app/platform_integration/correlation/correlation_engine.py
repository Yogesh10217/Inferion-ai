"""Cross-Phase Signal Correlation Engine (Phase 5.58)."""

import logging
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone

from app.platform_integration.models import (
    CrossPhaseSignal,
    CrossPhaseCorrelation,
    IntegrationPlatform,
    CausalRelationshipStatus,
)

logger = logging.getLogger(__name__)


class CrossPhaseCorrelationEngine:
    """Correlates signals across diverse intelligence platforms with strict non-causal defaults."""

    def correlate_signals(
        self,
        tenant_id: str,
        signals: List[CrossPhaseSignal],
        threshold: float = 0.5,
    ) -> List[CrossPhaseCorrelation]:
        """Evaluates concurrency, temporal proximity, and semantic relationships across signals."""
        correlations: List[CrossPhaseCorrelation] = []
        if len(signals) < 2:
            return correlations

        # Group signals by temporal window (e.g., 300s window)
        sorted_sigs = sorted(signals, key=lambda s: s.created_at)

        # Check cross-platform pairs
        for i in range(len(sorted_sigs)):
            for j in range(i + 1, len(sorted_sigs)):
                s1 = sorted_sigs[i]
                s2 = sorted_sigs[j]

                # Only correlate across distinct platforms
                if s1.source_platform == s2.source_platform:
                    continue

                # Calculate temporal closeness score (0.0 to 1.0)
                dt = abs((s2.created_at - s1.created_at).total_seconds())
                time_score = max(0.0, 1.0 - (dt / 3600.0))

                # Calculate severity alignment
                sev_score = 1.0 if s1.severity == s2.severity else 0.5

                # Combined correlation strength
                strength = round((time_score * 0.6) + (sev_score * 0.4), 3)

                if strength >= threshold:
                    corr_id = f"corr-{uuid.uuid4().hex[:10]}"
                    corr = CrossPhaseCorrelation(
                        correlation_id=corr_id,
                        tenant_id=tenant_id,
                        source_platforms=[s1.source_platform, s2.source_platform],
                        correlation_strength=strength,
                        confidence=round(min(s1.confidence, s2.confidence), 2),
                        is_causal=False,  # MANDATORY INVARIANT: Correlation does not imply causation
                        causal_status=CausalRelationshipStatus.HYPOTHESIZED,
                        correlated_signal_ids=[s1.signal_id, s2.signal_id],
                        explanation=f"Correlated {s1.source_platform.value} ({s1.signal_type}) with {s2.source_platform.value} ({s2.signal_type}) with strength {strength} (dt={dt:.1f}s)",
                        evidence_references=list(set(s1.evidence_references + s2.evidence_references)),
                    )
                    correlations.append(corr)

        return correlations
