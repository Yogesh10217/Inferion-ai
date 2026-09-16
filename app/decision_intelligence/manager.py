"""Master DecisionIntelligenceManager Orchestrator Subsystem."""

import logging
from typing import Any, Dict, Optional

from app.decision_intelligence.alternatives import AlternativeManager
from app.decision_intelligence.analytics import DecisionAnalyticsEngine
from app.decision_intelligence.approvals import DecisionApprovalManager
from app.decision_intelligence.assurance import DecisionAssuranceEngine
from app.decision_intelligence.billing import DecisionBillingTracker
from app.decision_intelligence.constraints import ConstraintManager
from app.decision_intelligence.context import DecisionContextBuilder, DecisionContextManager, DecisionContextType
from app.decision_intelligence.decision_options import DecisionOptionsRegistry
from app.decision_intelligence.decisions import DecisionLifecycleState, DecisionManager, DecisionType
from app.decision_intelligence.delegation import DecisionDelegationManager, DelegationTarget
from app.decision_intelligence.evidence import DecisionEvidenceManager, EvidenceReference, EvidenceStrength
from app.decision_intelligence.governance import DecisionGovernanceEngine
from app.decision_intelligence.human_review import DecisionHumanReviewEngine
from app.decision_intelligence.investigations import DecisionInvestigationEngine
from app.decision_intelligence.learning import DecisionLearningManager
from app.decision_intelligence.observability import DecisionMetricsCollector
from app.decision_intelligence.outcomes import DecisionOutcomeManager
from app.decision_intelligence.providers import DecisionIntelligenceProviderRegistry
from app.decision_intelligence.recommendations import RecommendationEngine
from app.decision_intelligence.remediation import DecisionRemediationEngine
from app.decision_intelligence.reproducibility import DecisionReproducibilityEngine
from app.decision_intelligence.risk import DecisionRiskManager
from app.decision_intelligence.scenarios import ScenarioManager
from app.decision_intelligence.scoring import DecisionScoringEngine
from app.decision_intelligence.simulation import DecisionSimulationEngine
from app.decision_intelligence.snapshots import DecisionSnapshotStore
from app.decision_intelligence.tradeoffs import TradeoffAnalyzer
from app.decision_intelligence.trust import DecisionTrustEngine
from app.decision_intelligence.uncertainty import DecisionUncertaintyEngine
from app.decision_intelligence.verification import DecisionVerificationEngine

logger = logging.getLogger(__name__)


class DecisionIntelligenceManager:
    """Master Orchestrator unifying all Decision Intelligence domain subsystems via Provider-based Decoupling."""

    def __init__(self, provider_registry: Optional[DecisionIntelligenceProviderRegistry] = None) -> None:
        self.provider_registry = provider_registry or DecisionIntelligenceProviderRegistry()

        self.context_builder = DecisionContextBuilder()
        self.context_manager = DecisionContextManager()

        self.evidence_manager = DecisionEvidenceManager()
        self.scenario_manager = ScenarioManager()
        self.constraint_manager = ConstraintManager()
        self.alternative_manager = AlternativeManager()
        self.options_registry = DecisionOptionsRegistry()
        self.tradeoff_analyzer = TradeoffAnalyzer()

        self.scoring_engine = DecisionScoringEngine()
        self.recommendation_engine = RecommendationEngine()

        self.risk_manager = DecisionRiskManager()
        self.trust_engine = DecisionTrustEngine()
        self.governance_engine = DecisionGovernanceEngine()

        self.decision_manager = DecisionManager()
        self.delegation_manager = DecisionDelegationManager()
        self.outcome_manager = DecisionOutcomeManager()
        self.learning_manager = DecisionLearningManager()

        self.uncertainty_engine = DecisionUncertaintyEngine()
        self.reproducibility_engine = DecisionReproducibilityEngine()
        self.simulation_engine = DecisionSimulationEngine()
        self.approval_manager = DecisionApprovalManager()
        self.human_review_engine = DecisionHumanReviewEngine()
        self.investigation_engine = DecisionInvestigationEngine()
        self.remediation_engine = DecisionRemediationEngine()
        self.verification_engine = DecisionVerificationEngine()
        self.assurance_engine = DecisionAssuranceEngine()
        self.snapshot_store = DecisionSnapshotStore()

        self.analytics_engine = DecisionAnalyticsEngine()
        self.metrics_collector = DecisionMetricsCollector()
        self.billing_tracker = DecisionBillingTracker()

        logger.info("[DECISION INTELLIGENCE MASTER] DecisionIntelligenceManager initialized cleanly with all domain subsystems and provider decoupling.")

    def run_full_decision_flow(
        self,
        tenant_id: str,
        title: str = "Enterprise AI Architecture Modernization",
        decision_type: DecisionType = DecisionType.CROSS_DOMAIN,
    ) -> Dict[str, Any]:
        """Runs complete end-to-end decision flow across strict decision lifecycle states."""

        # 1. Decision Creation & State: PROPOSED
        dec = self.decision_manager.create_decision(tenant_id, title, decision_type)

        # Transition: PROPOSED -> ANALYZING
        dec.transition_to(DecisionLifecycleState.ANALYZING, reason="Assembling cross-domain context")

        # 2. Context & Cross-Domain Signals via Provider Registry
        cross_domain_signals = []
        for domain, provider in self.provider_registry.list_providers().items():
            if hasattr(provider, "get_domain_signals"):
                cross_domain_signals.extend(provider.get_domain_signals(tenant_id))

        ctx = self.context_builder.assemble_context(
            tenant_id=tenant_id,
            title=title,
            description="Assess modernization of enterprise AI architecture.",
            context_type=DecisionContextType.CROSS_DOMAIN,
            architecture_ref="arch_001",
            compliance_ref="comp_001",
        )
        self.context_manager.create_context(ctx)
        dec.context_id = ctx.context_id

        # Transition: ANALYZING -> OPTIONS_IDENTIFIED
        dec.transition_to(DecisionLifecycleState.OPTIONS_IDENTIFIED, reason="Identifying decision options")

        # 3. Decision Options Identification
        opt1 = self.options_registry.add_option(
            decision_id=dec.decision_id,
            tenant_id=tenant_id,
            title="Cloud Native Migration",
            description="Migrate workloads to managed cloud-native platform",
            action_type="DELEGATE",
            target_system="OPERATIONS",
            estimated_cost=25000.0,
            reversibility="REVERSIBLE",
        )
        opt2 = self.options_registry.add_option(
            decision_id=dec.decision_id,
            tenant_id=tenant_id,
            title="In-Place Refactoring",
            description="Refactor existing monolith in-place",
            action_type="DELEGATE",
            target_system="DEVELOPMENT",
            estimated_cost=15000.0,
            reversibility="PARTIALLY_REVERSIBLE",
        )

        # Evidence
        ev_ref = EvidenceReference(
            source_subsystem="ARCHITECTURE",
            source_entity_id="arch_001",
            description="Verified system topology baseline.",
            strength=EvidenceStrength.STRONG,
        )
        ev_col = self.evidence_manager.collect_evidence(tenant_id, ctx.context_id, [ev_ref])
        dec.evidence_id = ev_col.collection_id

        # Transition: OPTIONS_IDENTIFIED -> RISK_ASSESSED
        dec.transition_to(DecisionLifecycleState.RISK_ASSESSED, reason="Evaluating risk and trust scores")

        # 4. Risk, Uncertainty & Simulation
        risk_prof = self.risk_manager.evaluate_decision_risk(tenant_id, ctx.context_id, architecture_risk=20.0, compliance_risk=20.0)
        trust_score = self.trust_engine.calculate_trust_score(tenant_id, ctx.context_id, architecture_trust=90.0, compliance_trust=90.0)
        uncert = self.uncertainty_engine.assess_uncertainty(dec.decision_id, tenant_id, evidence_quality_score=ev_col.quality_score)

        sim_result = self.simulation_engine.simulate_decision_options(
            decision_id=dec.decision_id,
            tenant_id=tenant_id,
            options=[opt1.model_dump(), opt2.model_dump()],
        )

        # Transition: RISK_ASSESSED -> POLICY_EVALUATED
        dec.transition_to(DecisionLifecycleState.POLICY_EVALUATED, reason="Evaluating governance policies")

        # 5. Policy Evaluation & Recommendation
        gov_dec = self.governance_engine.evaluate_decision_governance(
            tenant_id=tenant_id,
            decision_id=dec.decision_id,
            risk_score=risk_prof.overall_risk_score,
            trust_score=trust_score.overall_score,
            amount_usd=50000.0,
        )
        dec.governance_id = gov_dec.governance_id

        # Transition: POLICY_EVALUATED -> RECOMMENDED
        dec.transition_to(DecisionLifecycleState.RECOMMENDED, reason="Generating recommendation")

        rec = self.recommendation_engine.generate_recommendation(
            tenant_id=tenant_id,
            context_id=ctx.context_id,
            constraint_result=None,
            tradeoff_analysis=None,
            risk_score=risk_prof.overall_risk_score,
            trust_score=trust_score.overall_score,
            alternative_id=opt1.option_id,
        )
        dec.recommendation_id = rec.recommendation_id

        # 6. Approval & Delegation
        # Transition: RECOMMENDED -> REQUIRES_APPROVAL -> APPROVED
        dec.transition_to(DecisionLifecycleState.REQUIRES_APPROVAL, reason="Awaiting human approval for high-risk action")
        appr_rec = self.approval_manager.submit_approval(dec.decision_id, tenant_id, approver="security_admin@enterprise.local", approved=True)
        dec.transition_to(DecisionLifecycleState.APPROVED, reason="Approved by human reviewer")

        # Transition: APPROVED -> DELEGATED
        dec.transition_to(DecisionLifecycleState.DELEGATED, reason="Delegating to downstream execution platform")
        del_plan = self.delegation_manager.create_delegation_plan(tenant_id, dec.decision_id, DelegationTarget.PORTFOLIO_PLATFORM)
        delegated_plan = self.delegation_manager.delegate_execution(del_plan.delegation_id, tenant_id, "PortfolioPlatformManager")

        # Transition: DELEGATED -> VERIFIED
        dec.transition_to(DecisionLifecycleState.VERIFIED, reason="Verifying execution outcome")
        verif_rec = self.verification_engine.verify_delegation(dec.decision_id, tenant_id, delegated_plan.delegation_id)

        # 7. Reproducibility & Immutability
        repro_rec = self.reproducibility_engine.capture_reproducibility_record(
            decision_id=dec.decision_id,
            tenant_id=tenant_id,
            context_fingerprint=f"ctx_fp_{ctx.context_id}",
            evidence_hashes=[f"ev_hash_{ev_col.collection_id}"],
        )

        # Transition: VERIFIED -> CLOSED
        finalized_dec = self.decision_manager.finalize_decision(
            decision_id=dec.decision_id,
            tenant_id=tenant_id,
            risk_score=risk_prof.overall_risk_score,
            trust_score=trust_score.overall_score,
        )

        self.metrics_collector.increment("ai_decision_decisions_total")

        return {
            "decision": finalized_dec.model_dump(),
            "context": ctx.model_dump(),
            "evidence": ev_col.model_dump(),
            "simulation": sim_result.model_dump(),
            "uncertainty": uncert.model_dump(),
            "risk_profile": risk_prof.model_dump(),
            "trust_score": trust_score.model_dump(),
            "recommendation": rec.model_dump(),
            "governance": gov_dec.model_dump(),
            "approval": appr_rec.model_dump(),
            "delegation": delegated_plan.model_dump(),
            "verification": verif_rec.model_dump(),
            "reproducibility": repro_rec.model_dump(),
        }

    def get_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        report = self.analytics_engine.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()
        return {
            "status": "OPERATIONAL",
            "report": report.model_dump(),
            "metrics": metrics,
        }
