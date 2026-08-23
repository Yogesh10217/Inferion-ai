"""Master DecisionIntelligenceManager Orchestrator Subsystem."""

import logging
from typing import Dict, Any, Optional, List

from app.decision_intelligence.context import DecisionContextManager, DecisionContextBuilder, DecisionContextType, DecisionScope, DecisionPriority
from app.decision_intelligence.evidence import DecisionEvidenceManager, EvidenceReference, EvidenceStrength, EvidenceReliability
from app.decision_intelligence.scenarios import ScenarioManager, ScenarioType, ScenarioAssumption, ScenarioVariable
from app.decision_intelligence.constraints import ConstraintManager, DecisionConstraint, ConstraintType, ConstraintSeverity
from app.decision_intelligence.alternatives import AlternativeManager, AlternativeScore
from app.decision_intelligence.tradeoffs import TradeoffAnalyzer, Tradeoff, TradeoffDimension, TradeoffSeverity
from app.decision_intelligence.recommendations import RecommendationEngine, RecommendationType, DecisionRecommendation
from app.decision_intelligence.scoring import DecisionScoringEngine, DecisionScoreDimension
from app.decision_intelligence.risk import DecisionRiskManager, DecisionRiskDimension
from app.decision_intelligence.trust import DecisionTrustEngine, DecisionTrustDimension
from app.decision_intelligence.governance import DecisionGovernanceEngine, DecisionGovernanceStatus
from app.decision_intelligence.decisions import DecisionManager, EnterpriseDecision, DecisionType, DecisionStatus
from app.decision_intelligence.delegation import DecisionDelegationManager, DelegationTarget
from app.decision_intelligence.outcomes import DecisionOutcomeManager, OutcomeStatus
from app.decision_intelligence.learning import DecisionLearningManager
from app.decision_intelligence.analytics import DecisionAnalyticsEngine, DecisionReport
from app.decision_intelligence.observability import DecisionMetricsCollector
from app.decision_intelligence.billing import DecisionBillingTracker
from app.decision_intelligence.repositories import InMemoryDecisionRepository

logger = logging.getLogger(__name__)


class DecisionIntelligenceManager:
    """Master Orchestrator unifying all Decision Intelligence domain subsystems."""

    def __init__(self) -> None:
        self.context_builder = DecisionContextBuilder()
        self.context_manager = DecisionContextManager()

        self.evidence_manager = DecisionEvidenceManager()
        self.scenario_manager = ScenarioManager()
        self.constraint_manager = ConstraintManager()
        self.alternative_manager = AlternativeManager()
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

        self.analytics_engine = DecisionAnalyticsEngine()
        self.metrics_collector = DecisionMetricsCollector()
        self.billing_tracker = DecisionBillingTracker()

        logger.info("[DECISION INTELLIGENCE MASTER] DecisionIntelligenceManager initialized cleanly with all domain subsystems.")

    def run_full_decision_flow(
        self,
        tenant_id: str,
        title: str = "Enterprise AI Architecture Modernization",
        decision_type: DecisionType = DecisionType.CROSS_DOMAIN,
    ) -> Dict[str, Any]:
        """Runs complete end-to-end decision flow: Context -> Evidence -> Scenario -> Constraints -> Alternatives -> Trade-offs -> Risk -> Trust -> Recommendation -> Governance -> Approval -> Delegation -> Outcome -> Learning -> Finalization."""

        # 1. Decision Record & Context
        dec = self.decision_manager.create_decision(tenant_id, title, decision_type)
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

        # 2. Evidence Collection
        ev_ref = EvidenceReference(
            source_subsystem="ARCHITECTURE",
            source_entity_id="arch_001",
            description="Verified system topology baseline.",
            strength=EvidenceStrength.STRONG,
            metadata={"secret_token": "sk-secret-12345"},
        )
        ev_col = self.evidence_manager.collect_evidence(tenant_id, ctx.context_id, [ev_ref])
        dec.evidence_id = ev_col.collection_id

        # 3. Scenario & Alternatives & Tradeoffs
        scen = self.scenario_manager.create_scenario(tenant_id, ctx.context_id, "Cost-Optimized Modernization", scenario_type=ScenarioType.COST_OPTIMIZED)
        sim_scen = self.scenario_manager.simulate_scenario(scen.scenario_id, tenant_id)

        alt = self.alternative_manager.create_alternative(tenant_id, ctx.context_id, "Cloud Native Migration", "Migrate to managed services")
        tradeoff = Tradeoff(
            dimension=TradeoffDimension.OPERATIONAL_COMPLEXITY,
            gain_description="Higher scalability and lower infrastructure overhead.",
            sacrifice_description="Temporary operational transition complexity.",
            severity=TradeoffSeverity.MODERATE,
            is_negative_impact=True,
        )
        tradeoff_analysis = self.tradeoff_analyzer.analyze_tradeoffs(tenant_id, ctx.context_id, alt.alternative_id, [tradeoff])

        # 4. Constraints & Risk & Trust Evaluation
        const_result = self.constraint_manager.evaluate_constraints(
            tenant_id=tenant_id,
            context_id=ctx.context_id,
            observed_values={ConstraintType.RISK: 20.0, ConstraintType.TRUST: 90.0},
        )
        risk_prof = self.risk_manager.evaluate_decision_risk(tenant_id, ctx.context_id, architecture_risk=20.0, compliance_risk=20.0)
        trust_score = self.trust_engine.calculate_trust_score(tenant_id, ctx.context_id, architecture_trust=90.0, compliance_trust=90.0)

        # 5. Recommendation & Governance & Approval
        rec = self.recommendation_engine.generate_recommendation(
            tenant_id=tenant_id,
            context_id=ctx.context_id,
            constraint_result=const_result,
            tradeoff_analysis=tradeoff_analysis,
            risk_score=risk_prof.overall_risk_score,
            trust_score=trust_score.overall_score,
            alternative_id=alt.alternative_id,
        )
        dec.recommendation_id = rec.recommendation_id

        gov_dec = self.governance_engine.evaluate_decision_governance(
            tenant_id=tenant_id,
            decision_id=dec.decision_id,
            risk_score=risk_prof.overall_risk_score,
            trust_score=trust_score.overall_score,
            amount_usd=50000.0,
        )
        dec.governance_id = gov_dec.governance_id

        # 6. Delegation Plan
        del_plan = self.delegation_manager.create_delegation_plan(tenant_id, dec.decision_id, DelegationTarget.PORTFOLIO_PLATFORM)
        delegated_plan = self.delegation_manager.delegate_execution(del_plan.delegation_id, tenant_id, "PortfolioPlatformManager")

        # 7. Outcome & Learning
        outcome = self.outcome_manager.record_outcome(tenant_id, dec.decision_id, 100000.0, 110000.0)
        learning = self.learning_manager.process_outcome_learning(tenant_id, outcome)

        # 8. Finalize Decision (Immutable)
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
            "scenario": sim_scen.model_dump(),
            "alternative": alt.model_dump(),
            "tradeoffs": tradeoff_analysis.model_dump(),
            "risk_profile": risk_prof.model_dump(),
            "trust_score": trust_score.model_dump(),
            "recommendation": rec.model_dump(),
            "governance": gov_dec.model_dump(),
            "delegation": delegated_plan.model_dump(),
            "outcome": outcome.model_dump(),
            "learning": learning.model_dump(),
        }

    def get_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        report = self.analytics_engine.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()
        return {
            "status": "OPERATIONAL",
            "report": report.model_dump(),
            "metrics": metrics,
        }
