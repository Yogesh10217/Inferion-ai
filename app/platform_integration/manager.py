"""Thin Platform Integration Manager Facade (Phase 5.58)."""

import logging
from typing import List, Optional

from app.platform_contracts.delegation import DelegationRequest
from app.platform_integration.analytics import PlatformIntegrationAnalytics
from app.platform_integration.assurance.assurance_fabric import CrossPhaseAssuranceEngine
from app.platform_integration.assurance.confidence import CrossPhaseConfidenceEngine
from app.platform_integration.assurance.uncertainty import CrossPhaseUncertaintyEngine
from app.platform_integration.context.builder import (
    PlatformIntegrationContext,
    PlatformIntegrationContextBuilder,
)
from app.platform_integration.context.propagation import ContextPropagationEngine
from app.platform_integration.correlation.correlation_engine import CrossPhaseCorrelationEngine
from app.platform_integration.correlation.dependency_graph import CrossPhaseDependencyGraph
from app.platform_integration.correlation.risk_propagation import CrossPhaseRiskPropagationEngine
from app.platform_integration.delegation.coordinator import CrossPhaseDelegationCoordinator
from app.platform_integration.delegation.recommendations import CrossPhaseRecommendationEngine
from app.platform_integration.delegation.verification import CrossPhaseVerificationEngine
from app.platform_integration.events.coordinator import EventCoordinator
from app.platform_integration.exceptions import (
    IntegrationContextNotFoundException,
)
from app.platform_integration.governance.approvals import PlatformIntegrationApprovalManager
from app.platform_integration.governance.governance import PlatformIntegrationGovernanceEngine
from app.platform_integration.investigation.engine import CrossPhaseInvestigationEngine, CrossPhaseInvestigationResult
from app.platform_integration.investigation.explainability import PlatformIntegrationExplainabilityEngine
from app.platform_integration.lineage.graph import LineageGraph, LineageNode, LineageNodeType
from app.platform_integration.models import (
    CrossPhaseCorrelation,
    CrossPhaseRecommendation,
    CrossPhaseVerificationResult,
    PlatformAssurancePosture,
    TraceContext,
)
from app.platform_integration.observability import PlatformIntegrationObservability
from app.platform_integration.providers import (
    PlatformIntegrationProviderRegistry,
)
from app.platform_integration.repositories import (
    CorrelationRepository,
    IntegrationContextRepository,
    InvestigationRepository,
    RecommendationRepository,
)
from app.platform_integration.state.evidence import CrossPhaseEvidenceManager
from app.platform_integration.state.idempotency import PlatformIntegrationIdempotencyManager
from app.platform_integration.state.snapshots import (
    PlatformIntegrationSnapshotManager,
    PlatformIntegrationSnapshotRecord,
)

logger = logging.getLogger(__name__)


class PlatformIntegrationManager:
    """Thin orchestration facade across provider registry, specialized correlation, lineage, and verification engines."""

    def __init__(self) -> None:
        self.providers = PlatformIntegrationProviderRegistry()
        self.context_builder = PlatformIntegrationContextBuilder()
        self.propagation = ContextPropagationEngine()
        self.dep_graph = CrossPhaseDependencyGraph()
        self.correlation = CrossPhaseCorrelationEngine()
        self.risk_propagation = CrossPhaseRiskPropagationEngine(dep_graph=self.dep_graph)
        self.events = EventCoordinator()
        self.assurance = CrossPhaseAssuranceEngine()
        self.confidence = CrossPhaseConfidenceEngine()
        self.uncertainty = CrossPhaseUncertaintyEngine()
        self.investigation = CrossPhaseInvestigationEngine(dep_graph=self.dep_graph, registry=self.providers)
        self.explainability = PlatformIntegrationExplainabilityEngine()
        self.lineage = LineageGraph()
        self.governance = PlatformIntegrationGovernanceEngine()
        self.approvals = PlatformIntegrationApprovalManager()
        self.recommendations = CrossPhaseRecommendationEngine()
        self.delegation = CrossPhaseDelegationCoordinator(approval_manager=self.approvals)
        self.verification = CrossPhaseVerificationEngine()
        self.evidence = CrossPhaseEvidenceManager()
        self.snapshots = PlatformIntegrationSnapshotManager()
        self.idempotency = PlatformIntegrationIdempotencyManager()

        # Repositories
        self.context_repo = IntegrationContextRepository()
        self.correlation_repo = CorrelationRepository()
        self.investigation_repo = InvestigationRepository()
        self.recommendation_repo = RecommendationRepository()

        # Observability & Analytics
        self.observability = PlatformIntegrationObservability()
        self.analytics = PlatformIntegrationAnalytics()

        logger.info("[PLATFORM INTEGRATION MASTER] PlatformIntegrationManager initialized thin orchestration fabric.")

    # Context Collection & Building
    def build_context(
        self,
        tenant_id: str,
        trace_context: Optional[TraceContext] = None,
    ) -> PlatformIntegrationContext:
        self.observability.record_provider_request()
        provider_results = self.providers.collect_all_intelligence(tenant_id)
        ctx = self.context_builder.build_context(tenant_id, provider_results, trace_context)
        self.context_repo.save(ctx)

        # Register signals in lineage graph
        for s in ctx.signals:
            node = LineageNode(
                node_id=s.signal_id,
                node_type=LineageNodeType.SIGNAL,
                tenant_id=tenant_id,
                platform=s.source_platform.value,
                metadata={"signal_type": s.signal_type, "severity": s.severity},
            )
            self.lineage.add_node(node)

        return ctx

    def get_context(self, tenant_id: str, context_id: str) -> PlatformIntegrationContext:
        ctx = self.context_repo.get(tenant_id, context_id)
        if not ctx:
            raise IntegrationContextNotFoundException(f"Context '{context_id}' not found for tenant '{tenant_id}'.")
        return ctx

    # Cross-Phase Signal Correlation
    def correlate_signals(
        self,
        tenant_id: str,
        context_id: str,
        threshold: float = 0.5,
    ) -> List[CrossPhaseCorrelation]:
        ctx = self.get_context(tenant_id, context_id)
        corrs = self.correlation.correlate_signals(tenant_id, ctx.signals, threshold=threshold)
        for c in corrs:
            self.correlation_repo.save(c)
            self.observability.record_correlation()
        return corrs

    # Posture Evaluation
    def evaluate_assurance_posture(self, tenant_id: str) -> PlatformAssurancePosture:
        provider_results = self.providers.collect_all_intelligence(tenant_id)
        posture = self.assurance.evaluate_assurance_posture(tenant_id, provider_results)
        return posture

    # Investigation
    def run_investigation(
        self,
        tenant_id: str,
        root_platform: str,
        incident_description: str,
    ) -> CrossPhaseInvestigationResult:
        self.observability.record_investigation()
        res = self.investigation.investigate(tenant_id, root_platform, incident_description)
        self.investigation_repo.save(res)
        return res

    # Recommendations
    def generate_recommendations(
        self,
        tenant_id: str,
        degraded_platforms: List[str],
    ) -> List[CrossPhaseRecommendation]:
        self.observability.record_recommendation()
        recs = self.recommendations.generate_recommendations(tenant_id, degraded_platforms)
        for r in recs:
            self.recommendation_repo.save(r)
            # Add to lineage graph
            r_node = LineageNode(
                node_id=r.recommendation_id,
                node_type=LineageNodeType.RECOMMENDATION,
                tenant_id=tenant_id,
                platform=r.target_platform.value,
                metadata={"action": r.action, "risk": r.risk_level.value},
            )
            self.lineage.add_node(r_node)
        return recs

    # Delegation
    def delegate_action(
        self,
        tenant_id: str,
        recommendation_id: str,
        approval_id: Optional[str] = None,
        approval_token: Optional[str] = None,
    ) -> DelegationRequest:
        rec = self.recommendation_repo.get(tenant_id, recommendation_id)
        if not rec:
            raise KeyError(f"Recommendation '{recommendation_id}' not found.")

        gov_decision = self.governance.evaluate_governance(tenant_id, rec.action, rec.risk_level)
        del_req = self.delegation.create_delegation(
            tenant_id=tenant_id,
            recommendation=rec,
            governance_decision=gov_decision,
            approval_id=approval_id,
            approval_token=approval_token,
        )
        self.observability.record_delegation()

        # Add to lineage graph and link to recommendation
        del_node = LineageNode(
            node_id=del_req.delegation_id,
            node_type=LineageNodeType.DELEGATION,
            tenant_id=tenant_id,
            platform=rec.target_platform.value,
            metadata={"action": del_req.action, "target": del_req.target.value},
        )
        self.lineage.add_node(del_node)
        self.lineage.add_edge(rec.recommendation_id, del_req.delegation_id)

        return del_req

    # Verification
    def verify_delegation(
        self,
        tenant_id: str,
        delegation_id: str,
        pre_score: float,
        post_score: float,
        required_delta: float = 0.05,
    ) -> CrossPhaseVerificationResult:
        self.observability.record_verification()
        res = self.verification.verify_outcome(tenant_id, delegation_id, pre_score, post_score, required_delta)

        # Add to lineage graph and link to delegation
        v_node = LineageNode(
            node_id=res.verification_id,
            node_type=LineageNodeType.VERIFICATION,
            tenant_id=tenant_id,
            platform="PLATFORM_INTEGRATION",
            metadata={"verified": res.verified, "delta": res.improvement_delta},
        )
        self.lineage.add_node(v_node)
        if delegation_id in self.lineage.nodes:
            self.lineage.add_edge(delegation_id, res.verification_id)

        return res

    # Snapshots
    def capture_snapshot(self, tenant_id: str) -> PlatformIntegrationSnapshotRecord:
        ctx = self.build_context(tenant_id)
        posture = self.evaluate_assurance_posture(tenant_id)
        return self.snapshots.capture_snapshot(
            tenant_id=tenant_id,
            active_platforms=ctx.active_platforms,
            context_fingerprint=ctx.fingerprint,
            overall_assurance_score=posture.overall_score,
            domain_payload={"posture": posture.posture, "trust_band": posture.trust_band},
        )
