"""Bounded Context Builder and Fingerprinting for Platform Integration (Phase 5.58)."""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.platform_integration.models import (
    CrossPhaseAssessment,
    CrossPhaseFinding,
    CrossPhaseSignal,
    TraceContext,
)
from app.platform_integration.providers import PlatformProviderResult

logger = logging.getLogger(__name__)


@dataclass
class BoundedContextPolicy:
    """Policy governing boundaries of cross-phase integrated contexts."""

    max_platforms: int = 10
    max_signals: int = 500
    max_age_hours: int = 24
    max_evidence_references: int = 100


@dataclass
class PlatformIntegrationContext:
    context_id: str
    tenant_id: str
    trace_context: TraceContext
    signals: List[CrossPhaseSignal] = field(default_factory=list)
    findings: List[CrossPhaseFinding] = field(default_factory=list)
    assessments: List[CrossPhaseAssessment] = field(default_factory=list)
    active_platforms: List[str] = field(default_factory=list)
    fingerprint: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PlatformIntegrationContextBuilder:
    """Constructs bounded, cryptographically fingerprinted cross-phase integration contexts."""

    def __init__(self, policy: Optional[BoundedContextPolicy] = None) -> None:
        self.policy = policy or BoundedContextPolicy()

    def build_context(
        self,
        tenant_id: str,
        provider_results: Dict[str, PlatformProviderResult],
        trace_context: Optional[TraceContext] = None,
    ) -> PlatformIntegrationContext:
        ctx = trace_context or TraceContext(tenant_id=tenant_id)
        cid = f"ctx-{uuid.uuid4().hex[:12]}"

        signals: List[CrossPhaseSignal] = []
        findings: List[CrossPhaseFinding] = []
        assessments: List[CrossPhaseAssessment] = []
        active_platforms: List[str] = []

        from app.platform_integration.context.normalization import DomainNormalizer

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=self.policy.max_age_hours)

        for p_name, p_res in provider_results.items():
            if len(active_platforms) >= self.policy.max_platforms:
                logger.warning(f"Max platforms limit ({self.policy.max_platforms}) reached. Skipping {p_name}.")
                break

            if p_res.status in ("SUCCESS", "DEGRADED"):
                active_platforms.append(p_name)
                data = p_res.data

                # Ingest & normalize signals
                for s in data.get("signals", []):
                    if len(signals) >= self.policy.max_signals:
                        break
                    norm_sig = DomainNormalizer.normalize_signal(tenant_id, p_name, s, ctx)
                    if norm_sig.created_at >= cutoff:
                        signals.append(norm_sig)

                # Ingest & normalize findings
                for f in data.get("findings", []):
                    norm_find = DomainNormalizer.normalize_finding(tenant_id, p_name, f, ctx)
                    findings.append(norm_find)

                # Ingest & normalize assessment
                score = data.get("score", 0.9)
                posture = data.get("status", "ASSURED")
                norm_ass = DomainNormalizer.normalize_assessment(
                    tenant_id,
                    p_name,
                    {
                        "score": score,
                        "posture": posture,
                        "confidence": p_res.confidence,
                        "uncertainty": p_res.uncertainty,
                    },
                    ctx,
                )
                assessments.append(norm_ass)

        # Deterministic SHA-256 fingerprint
        fingerprint = self._compute_fingerprint(tenant_id, active_platforms, signals, findings)

        return PlatformIntegrationContext(
            context_id=cid,
            tenant_id=tenant_id,
            trace_context=ctx,
            signals=signals,
            findings=findings,
            assessments=assessments,
            active_platforms=active_platforms,
            fingerprint=fingerprint,
        )

    def _compute_fingerprint(
        self,
        tenant_id: str,
        platforms: List[str],
        signals: List[CrossPhaseSignal],
        findings: List[CrossPhaseFinding],
    ) -> str:
        body = {
            "tenant_id": tenant_id,
            "platforms": sorted(platforms),
            "signal_ids": sorted([s.signal_id for s in signals]),
            "finding_ids": sorted([f.finding_id for f in findings]),
        }
        raw = json.dumps(body, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
