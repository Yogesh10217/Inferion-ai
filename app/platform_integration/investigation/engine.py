"""Dynamic Graph-Based Cross-Phase Investigation Engine (Phase 5.58)."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from app.platform_integration.correlation.dependency_graph import CrossPhaseDependencyGraph
from app.platform_integration.models import (
    CrossPhaseFinding,
    TraceContext,
)
from app.platform_integration.providers import PlatformIntegrationProviderRegistry, PlatformProviderResult

logger = logging.getLogger(__name__)


@dataclass
class InvestigationTimelineEntry:
    timestamp: datetime
    platform: str
    phase_action: str
    summary: str


@dataclass
class InvestigationEvidenceBundle:
    evidence_bundle_id: str
    collected_evidence_ids: List[str]
    source_platforms: List[str]


@dataclass
class CrossPhaseInvestigationResult:
    investigation_id: str
    tenant_id: str
    root_platform: str
    traversed_platforms: List[str]
    timeline: List[InvestigationTimelineEntry]
    evidence_bundle: InvestigationEvidenceBundle
    findings: List[CrossPhaseFinding]
    conclusion: str
    confidence: float
    trace_context: TraceContext
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CrossPhaseInvestigationEngine:
    """Dynamically traverses platforms using dependency topology to investigate root incidents."""

    def __init__(
        self,
        dep_graph: Optional[CrossPhaseDependencyGraph] = None,
        registry: Optional[PlatformIntegrationProviderRegistry] = None,
    ) -> None:
        self.dep_graph = dep_graph or CrossPhaseDependencyGraph()
        self.registry = registry or PlatformIntegrationProviderRegistry()

    def investigate(
        self,
        tenant_id: str,
        root_platform: str,
        initial_incident_description: str,
        trace_context: Optional[TraceContext] = None,
    ) -> CrossPhaseInvestigationResult:
        inv_id = f"inv-{uuid.uuid4().hex[:12]}"
        ctx = trace_context or TraceContext(tenant_id=tenant_id, source_platform=root_platform)

        # Dynamic graph-based discovery of relevant platforms
        traversed = self.dep_graph.resolve_relevant_platforms(root_platform)

        timeline: List[InvestigationTimelineEntry] = []
        timeline.append(
            InvestigationTimelineEntry(
                timestamp=datetime.now(timezone.utc),
                platform=root_platform.upper(),
                phase_action="TRIGGER_INCIDENT",
                summary=initial_incident_description,
            )
        )

        all_findings: List[CrossPhaseFinding] = []
        all_evidence_ids: List[str] = []

        from app.platform_integration.context.normalization import DomainNormalizer

        for p_name in traversed:
            try:
                provider = self.registry.get_provider(p_name)
                res: PlatformProviderResult = provider.collect_intelligence(tenant_id)
                timeline.append(
                    InvestigationTimelineEntry(
                        timestamp=datetime.now(timezone.utc),
                        platform=p_name,
                        phase_action="QUERY_INTELLIGENCE",
                        summary=f"Queried {p_name} - status: {res.status}, score: {res.data.get('score', 'N/A')}",
                    )
                )

                for f in res.data.get("findings", []):
                    norm_f = DomainNormalizer.normalize_finding(tenant_id, p_name, f, ctx)
                    all_findings.append(norm_f)
                    all_evidence_ids.extend(norm_f.evidence_references)

                for ev in provider.collect_evidence(tenant_id):
                    if "evidence_id" in ev:
                        all_evidence_ids.append(ev["evidence_id"])

            except Exception as e:
                logger.warning(f"Failed to query {p_name} during investigation: {e}")
                timeline.append(
                    InvestigationTimelineEntry(
                        timestamp=datetime.now(timezone.utc),
                        platform=p_name,
                        phase_action="PROVIDER_FAILURE",
                        summary=f"Fault isolated for {p_name}: {e}",
                    )
                )

        ev_bundle = InvestigationEvidenceBundle(
            evidence_bundle_id=f"evb-{uuid.uuid4().hex[:10]}",
            collected_evidence_ids=list(set(all_evidence_ids)),
            source_platforms=traversed,
        )

        conclusion = (
            f"Cross-phase investigation originating from {root_platform.upper()} dynamically traversed "
            f"{len(traversed)} platforms ({', '.join(traversed)}). Found {len(all_findings)} related findings "
            f"with {len(ev_bundle.collected_evidence_ids)} corroborating evidence references."
        )

        return CrossPhaseInvestigationResult(
            investigation_id=inv_id,
            tenant_id=tenant_id,
            root_platform=root_platform.upper(),
            traversed_platforms=traversed,
            timeline=timeline,
            evidence_bundle=ev_bundle,
            findings=all_findings,
            conclusion=conclusion,
            confidence=0.88,
            trace_context=ctx,
        )
