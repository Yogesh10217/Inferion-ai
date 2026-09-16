"""
Central Subsystem Orchestrator Manager for Phase 5.51 Enterprise AI Unified Intelligence.

Coordinates cross-domain intelligence pipelines, signal ingestion, context fusion, correlation,
causal reasoning, situation awareness, risk propagation, assurance, recommendations,
governance evaluation, autonomous delegation, evidence creation, and observability.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.unified_intelligence.analytics import CrossDomainAnalyticsEngine, UnifiedAnalyticsSummary
from app.unified_intelligence.assurance_coordination import CrossDomainAssuranceCoordinator, UnifiedAssurancePosture
from app.unified_intelligence.billing import IntelligenceBillingEngine, UnifiedBillingRecord
from app.unified_intelligence.causal_analysis import CausalAnalysisEngine, CausalHypothesis
from app.unified_intelligence.context_fusion import ContextFusionEngine, UnifiedContext, UnifiedContextPolicy
from app.unified_intelligence.coordination import CoordinationPlan, CoordinationPlannerEngine
from app.unified_intelligence.correlation import CrossDomainCorrelationEngine
from app.unified_intelligence.delegation import AutonomousDelegationEngine
from app.unified_intelligence.dependency_intelligence import DependencyIntelligenceEngine
from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.evidence import SHA256EvidenceLedgerEngine
from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException,
)
from app.unified_intelligence.governance import GovernanceEvaluationResult, GovernancePolicyEvaluatorEngine
from app.unified_intelligence.idempotency import IdempotencyEngine
from app.unified_intelligence.impact import UnifiedImpactEngine
from app.unified_intelligence.investigations import UnifiedInvestigation, UnifiedInvestigationEngine
from app.unified_intelligence.learning import AdvisoryLearningEngine
from app.unified_intelligence.normalization_contracts import UnifiedDomainInput
from app.unified_intelligence.observability import UnifiedObservabilityEngine
from app.unified_intelligence.providers import BaseIntelligenceProvider, IntelligenceProviderRegistry
from app.unified_intelligence.recommendations import UnifiedRecommendation, UnifiedRecommendationEngine
from app.unified_intelligence.remediation import CrossDomainRemediationCoordinator
from app.unified_intelligence.repositories import UnifiedIntelligenceRepository
from app.unified_intelligence.risk import UnifiedRiskAssessment, UnifiedRiskEngine
from app.unified_intelligence.risk_propagation import RiskPropagationEngine
from app.unified_intelligence.signal_normalization import SignalNormalizationEngine
from app.unified_intelligence.signals import UnifiedSignal
from app.unified_intelligence.situation_awareness import EnterpriseSituation, SituationAwarenessEngine
from app.unified_intelligence.snapshots import UnifiedSnapshotGenerator
from app.unified_intelligence.timeline import UnifiedTimelineEngine
from app.unified_intelligence.trust import CrossDomainTrustEngine, UnifiedTrustAssessment
from app.unified_intelligence.verification import DelegationVerificationEngine

logger = logging.getLogger(__name__)


class UnifiedIntelligenceManager:
    """
    Central Subsystem Manager for Phase 5.51 Enterprise AI Unified Intelligence.
    Acts as orchestrator, delegating business logic to modular sub-engines & coordinators.
    """

    def __init__(
        self,
        repository: Optional[UnifiedIntelligenceRepository] = None,
        provider_registry: Optional[IntelligenceProviderRegistry] = None
    ):
        self.repository = repository or UnifiedIntelligenceRepository()
        self.provider_registry = provider_registry or IntelligenceProviderRegistry()

        # Engine instances
        self.normalization_engine = SignalNormalizationEngine()
        self.context_fusion_engine = ContextFusionEngine()
        self.correlation_engine = CrossDomainCorrelationEngine()
        self.causal_engine = CausalAnalysisEngine()
        self.dependency_engine = DependencyIntelligenceEngine()
        self.risk_propagation_engine = RiskPropagationEngine()
        self.situation_engine = SituationAwarenessEngine()
        self.timeline_engine = UnifiedTimelineEngine()
        self.impact_engine = UnifiedImpactEngine()
        self.risk_engine = UnifiedRiskEngine()
        self.assurance_coordinator = CrossDomainAssuranceCoordinator()
        self.trust_engine = CrossDomainTrustEngine()
        self.recommendation_engine = UnifiedRecommendationEngine()
        self.coordination_planner = CoordinationPlannerEngine()
        self.governance_evaluator = GovernancePolicyEvaluatorEngine()
        self.investigation_engine = UnifiedInvestigationEngine()
        self.remediation_coordinator = CrossDomainRemediationCoordinator()
        self.delegation_engine = AutonomousDelegationEngine()
        self.verification_engine = DelegationVerificationEngine()
        self.evidence_ledger = SHA256EvidenceLedgerEngine()
        self.snapshot_generator = UnifiedSnapshotGenerator()
        self.learning_engine = AdvisoryLearningEngine()
        self.analytics_engine = CrossDomainAnalyticsEngine()
        self.observability = UnifiedObservabilityEngine()
        self.billing_engine = IntelligenceBillingEngine()
        self.idempotency = IdempotencyEngine()

    def register_provider(self, domain: IntelligenceDomain, provider: BaseIntelligenceProvider) -> None:
        """Register a domain intelligence provider contract."""
        self.provider_registry.register_provider(domain, provider)

    def ingest_domain_input(
        self,
        tenant_id: str,
        domain_input: UnifiedDomainInput,
        idempotency_key: Optional[str] = None
    ) -> UnifiedSignal:
        """
        Ingests a standardized domain input, normalizes it, enforces idempotency,
        stores the resulting unified signal, and records metrics & usage.
        """
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        # Idempotency check
        key = idempotency_key or domain_input.idempotency_key
        if key and self.idempotency.is_duplicate(tenant_id, key):
            cached = self.idempotency.get_cached_result(tenant_id, key)
            if cached and isinstance(cached, UnifiedSignal):
                return cached

        normalized = self.normalization_engine.normalize_input(domain_input)
        sig = UnifiedSignal.from_normalized_signal(normalized)

        # Persistence
        self.repository.save_signal(tenant_id, sig)

        # Idempotency registration
        if key:
            self.idempotency.register_execution(tenant_id, key, sig)

        # Metrics and billing
        domain_str = sig.domain.value if hasattr(sig.domain, 'value') else str(sig.domain)
        self.observability.record_signal_processed(tenant_id, domain_str)
        self.billing_engine.record_usage(tenant_id, signals=1)

        return sig

    def fuse_context(
        self,
        tenant_id: str,
        policy: Optional[UnifiedContextPolicy] = None
    ) -> UnifiedContext:
        """Fuse available domain signals into a bounded UnifiedContext."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        signals = self.repository.list_signals(tenant_id)
        context = self.context_fusion_engine.fuse_context(tenant_id, signals, policy)
        return context

    def detect_situations(
        self,
        tenant_id: str,
        policy: Optional[UnifiedContextPolicy] = None
    ) -> List[EnterpriseSituation]:
        """
        Main intelligence pipeline: fuses context, correlates signals, analyzes causality,
        evaluates dependencies & risk propagation, and detects active EnterpriseSituations.
        """
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        context = self.fuse_context(tenant_id, policy)
        if not context.signals:
            return []

        correlations = self.correlation_engine.correlate_context(context)

        # Build causal hypotheses
        hypotheses: List[CausalHypothesis] = []
        for corr in correlations:
            hypotheses.extend(self.causal_engine.hypothesize_causality(tenant_id, corr))

        # Detect situations
        situations = self.situation_engine.evaluate_situations(context, correlations, hypotheses)

        # Save situations and update metrics
        for sit in situations:
            self.repository.save_situation(tenant_id, sit)

            # Evidentiary proof creation
            self.evidence_ledger.create_evidence(
                tenant_id=tenant_id,
                source_domain="unified_intelligence",
                payload=sit.to_dict()
            )

            sev_str = sit.severity.value if hasattr(sit.severity, 'value') else str(sit.severity)
            self.observability.record_situation_detected(tenant_id, sev_str)
            self.billing_engine.record_usage(tenant_id, situations=1, correlations=len(correlations))

        return situations

    def evaluate_risk(self, tenant_id: str) -> UnifiedRiskAssessment:
        """Evaluate holistic cross-domain risk score."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        signals = self.repository.list_signals(tenant_id)
        assessment = self.risk_engine.evaluate_risk(tenant_id, signals)
        self.observability.record_risk_score(tenant_id, assessment.overall_risk_score)
        return assessment

    def evaluate_assurance(self, tenant_id: str) -> UnifiedAssurancePosture:
        """Evaluate multi-domain enterprise assurance posture."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        # Collect domain assurance scores from registered providers
        provider_map = self.provider_registry.list_providers()
        domain_assurance: Dict[str, float] = {}

        for dom, prov in provider_map.items():
            try:
                assr = prov.get_assurance(tenant_id)
                domain_assurance[dom.value] = assr.get("score", 0.85)
            except Exception as e:
                logger.warning(f"Error calling provider for domain {dom.value}: {e}")
                # Fault isolation: missing/failing provider falls back cleanly
                domain_assurance[dom.value] = 0.70

        posture = self.assurance_coordinator.evaluate_assurance_posture(tenant_id, domain_assurance)
        self.observability.record_assurance_score(tenant_id, posture.overall_assurance_score)
        return posture

    def evaluate_trust(self, tenant_id: str, entity_reference: str) -> UnifiedTrustAssessment:
        """Evaluate cross-domain trust assessment for a specific entity."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        return self.trust_engine.evaluate_entity_trust(tenant_id, entity_reference, {})

    def generate_recommendations(
        self,
        tenant_id: str,
        situation_id: str
    ) -> List[UnifiedRecommendation]:
        """Generate prioritized cross-domain recommendations for a situation."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        sit = self.repository.get_situation(tenant_id, situation_id)
        if not sit:
            raise InvalidUnifiedIntelligenceInputException(f"Situation {situation_id} not found for tenant {tenant_id}")

        recs = self.recommendation_engine.generate_recommendations_for_situation(tenant_id, sit)
        for r in recs:
            self.repository.save_recommendation(tenant_id, r)
        return recs

    def build_coordination_plan(
        self,
        tenant_id: str,
        recommendation_id: str
    ) -> CoordinationPlan:
        """Build a multi-step execution coordination plan for a recommendation."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        recs = self.repository.list_recommendations(tenant_id)
        target_rec = next((r for r in recs if r.recommendation_id == recommendation_id), None)
        if not target_rec:
            raise InvalidUnifiedIntelligenceInputException(f"Recommendation {recommendation_id} not found.")

        return self.coordination_planner.build_plan_for_recommendation(tenant_id, target_rec)

    def evaluate_governance(
        self,
        tenant_id: str,
        recommendation: UnifiedRecommendation,
        approved_by: Optional[str] = None
    ) -> GovernanceEvaluationResult:
        """
        Evaluate governance policies. Raises HighRiskUnifiedActionRequiresApprovalException if unapproved.
        """
        return self.governance_evaluator.evaluate_recommendation(tenant_id, recommendation, approved_by)

    def execute_delegation(
        self,
        tenant_id: str,
        plan: CoordinationPlan,
        step_id: str,
        approved_by: Optional[str] = None,
        requestor_id: str = "unified_intelligence_manager"
    ) -> Dict[str, Any]:
        """
        Translates a coordination step into a DelegationRequest, ensuring governance approval gates pass.
        """
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if plan.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch in delegation: expected {tenant_id}, got {plan.tenant_id}"
            )

        step = next((s for s in plan.steps if s.step_id == step_id), None)
        if not step:
            raise InvalidUnifiedIntelligenceInputException(f"Step {step_id} not found in plan {plan.plan_id}")

        # Governance gate check
        self.governance_evaluator.evaluate_coordination_plan(tenant_id, plan, approved_by)

        delegation_req = self.delegation_engine.create_delegation_request(tenant_id, plan, step, requestor_id)

        return {
            "status": "DELEGATED",
            "delegation_request": delegation_req.to_dict(),
            "plan_id": plan.plan_id,
            "step_id": step.step_id
        }

    def create_investigation(
        self,
        tenant_id: str,
        situation_id: str,
        title: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> UnifiedInvestigation:
        """Create a new cross-domain investigation context for a situation."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        sit = self.repository.get_situation(tenant_id, situation_id)
        if not sit:
            raise InvalidUnifiedIntelligenceInputException(f"Situation {situation_id} not found.")

        inv = self.investigation_engine.create_investigation_for_situation(
            tenant_id, sit, title=title, assigned_to=assigned_to
        )
        self.repository.save_investigation(tenant_id, inv)
        return inv

    def generate_snapshot(self, tenant_id: str) -> Any:
        """Generates a full cross-domain state snapshot."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        signals = [s.to_dict() for s in self.repository.list_signals(tenant_id)]
        situations = [s.to_dict() for s in self.repository.list_situations(tenant_id)]

        data = {
            "signals": signals,
            "situations": situations,
            "snapshot_timestamp": datetime.utcnow().isoformat()
        }
        return self.snapshot_generator.generate_snapshot(tenant_id, data)

    def get_analytics_summary(self, tenant_id: str) -> UnifiedAnalyticsSummary:
        """Compute executive analytics summary for unified intelligence."""
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        signals = self.repository.list_signals(tenant_id)
        situations = self.repository.list_situations(tenant_id)
        return self.analytics_engine.compute_summary(tenant_id, len(signals), situations)

    def get_billing(self, tenant_id: str) -> UnifiedBillingRecord:
        """Retrieve usage billing record for tenant."""
        return self.billing_engine.get_tenant_billing(tenant_id)
