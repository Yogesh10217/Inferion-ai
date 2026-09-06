"""Master orchestrator for Enterprise AI Decision Intelligence & Autonomous Planning."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.decision_governance.decisions import DecisionManager, Decision, DecisionType, DecisionStatus, DecisionOutcome, DecisionContext, DecisionPriority
from app.decision_governance.planning import DecisionPlanningManager, DecisionPlan, DecisionPlanStep
from app.decision_governance.recommendations import DecisionRecommendationManager, DecisionRecommendation, RecommendationType
from app.decision_governance.alternatives import DecisionAlternativeManager, DecisionAlternative
from app.decision_governance.scenarios import DecisionScenarioManager, DecisionScenario, ScenarioType
from app.decision_governance.simulation import DecisionSimulationManager, DecisionSimulation, SimulationInput
from app.decision_governance.optimization import DecisionOptimizationManager, DecisionOptimization, OptimizationObjective
from app.decision_governance.conflicts import DecisionConflictManager, DecisionConflict
from app.decision_governance.priorities import DecisionPriorityManager, DecisionPriorityAssessment
from app.decision_governance.risk import DecisionRiskManager, DecisionRiskAssessment
from app.decision_governance.impact import DecisionImpactManager, ImpactAssessment
from app.decision_governance.confidence import DecisionConfidenceManager, ConfidenceAssessment
from app.decision_governance.explainability import DecisionExplainabilityManager, DecisionExplanation
from app.decision_governance.evidence import DecisionEvidenceManager, DecisionEvidenceBundle, DecisionEvidence
from app.decision_governance.signals import DecisionSignalManager, DecisionSignal, DecisionSignalSource, DecisionSignalType
from app.decision_governance.correlation import DecisionCorrelationManager, DecisionCorrelation
from app.decision_governance.cross_domain import CrossDomainIntelligenceManager, CrossDomainContext
from app.decision_governance.governance import DecisionGovernanceEngine, DecisionGovernanceRequest, DecisionGovernanceResult
from app.decision_governance.delegation import DecisionDelegationManager, DecisionDelegationPlan, DecisionDelegationAction
from app.decision_governance.verification import DecisionVerificationManager, DecisionVerification
from app.decision_governance.assurance import DecisionAssuranceManager, DecisionAssuranceAssessment
from app.decision_governance.investigations import DecisionInvestigationManager, DecisionInvestigation
from app.decision_governance.trust import DecisionTrustEngine
from app.decision_governance.learning import DecisionLearningManager, DecisionLearningRecord
from app.decision_governance.analytics import DecisionGovernanceAnalyticsEngine, DecisionAnalyticsReport
from app.decision_governance.observability import DecisionGovernanceMetrics
from app.decision_governance.billing import DecisionBillingTracker
from app.decision_governance.snapshots import DecisionSnapshotManager
from app.decision_governance.repositories import DecisionGovernanceRepository

from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    DecisionNotFoundException,
    HighRiskDecisionRequiresApprovalException,
    ImmutableDecisionRecordException,
)


class DecisionGovernanceManager:
    """Master orchestrator for Phase 5.45 Decision Governance platform."""

    def __init__(self) -> None:
        self.decisions = DecisionManager()
        self.planning = DecisionPlanningManager()
        self.recommendations = DecisionRecommendationManager()
        self.alternatives = DecisionAlternativeManager()
        self.scenarios = DecisionScenarioManager()
        self.simulation = DecisionSimulationManager()
        self.optimization = DecisionOptimizationManager()
        self.conflicts = DecisionConflictManager()
        self.priorities = DecisionPriorityManager()
        self.risk = DecisionRiskManager()
        self.impact = DecisionImpactManager()
        self.confidence = DecisionConfidenceManager()
        self.explainability = DecisionExplainabilityManager()
        self.evidence = DecisionEvidenceManager()
        self.signals = DecisionSignalManager()
        self.correlation = DecisionCorrelationManager()
        self.cross_domain = CrossDomainIntelligenceManager()
        self.governance = DecisionGovernanceEngine()
        self.delegation = DecisionDelegationManager()
        self.verification = DecisionVerificationManager()
        self.assurance = DecisionAssuranceManager()
        self.investigations = DecisionInvestigationManager()
        self.trust = DecisionTrustEngine()
        self.learning = DecisionLearningManager()
        self.analytics = DecisionGovernanceAnalyticsEngine()
        self.observability = DecisionGovernanceMetrics()
        self.billing = DecisionBillingTracker()
        self.snapshots = DecisionSnapshotManager()
        self.repository = DecisionGovernanceRepository[Decision]()

    def create_decision(
        self,
        tenant_id: str,
        title: str,
        decision_type: DecisionType = DecisionType.OPERATIONAL,
        description: str = "",
        context: Optional[DecisionContext] = None,
        priority: DecisionPriority = DecisionPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Decision:
        if not context:
            context = DecisionContext(tenant_id=tenant_id)
        decision = self.decisions.create_decision(
            tenant_id=tenant_id,
            title=title,
            decision_type=decision_type,
            context=context,
            description=description,
            priority=priority,
            metadata=metadata,
        )
        self.repository.save(tenant_id, decision.decision_id, decision)
        self.observability.decisions_created.labels(tenant_id=tenant_id, decision_type=decision_type.value).inc()
        return decision

    def get_decision(self, decision_id: str, tenant_id: str) -> Decision:
        return self.repository.get(tenant_id, decision_id)

    def analyze_and_governed_evaluate(self, decision_id: str, tenant_id: str) -> DecisionGovernanceResult:
        decision = self.get_decision(decision_id, tenant_id)
        self.decisions.update_status(decision_id, tenant_id, DecisionStatus.ANALYZING)

        # Run risk assessment
        risk_assessment = self.risk.assess_risk(tenant_id, decision_id)
        decision.risk_score = risk_assessment.profile.overall_risk_score

        # Run confidence assessment
        conf_assessment = self.confidence.assess_confidence(tenant_id, decision_id)
        decision.confidence = conf_assessment.confidence.confidence_score

        # Governance evaluation
        gov_req = DecisionGovernanceRequest(
            tenant_id=tenant_id,
            decision_id=decision_id,
            action_type=decision.decision_type.value,
            risk_score=decision.risk_score,
        )
        gov_res = self.governance.evaluate_decision_governance(gov_req)

        if gov_res.requires_human_approval:
            self.decisions.update_status(decision_id, tenant_id, DecisionStatus.REQUIRES_APPROVAL, outcome=DecisionOutcome.REQUIRE_APPROVAL)
        else:
            self.decisions.update_status(decision_id, tenant_id, DecisionStatus.RECOMMENDED, outcome=gov_res.outcome)

        self.repository.save(tenant_id, decision.decision_id, decision)
        return gov_res

    def approve_decision(self, decision_id: str, tenant_id: str, approver_id: str = "human_admin") -> Decision:
        decision = self.get_decision(decision_id, tenant_id)
        approved = self.decisions.update_status(decision_id, tenant_id, DecisionStatus.APPROVED, outcome=DecisionOutcome.ALLOW)
        approved.metadata["approved_by"] = approver_id
        approved.metadata["approved_at"] = datetime.now(timezone.utc).isoformat()
        self.repository.save(tenant_id, decision_id, approved)
        self.observability.decisions_approved.labels(tenant_id=tenant_id).inc()
        return approved

    def delegate_decision(
        self, decision_id: str, tenant_id: str, actions: List[DecisionDelegationAction]
    ) -> DecisionDelegationPlan:
        decision = self.get_decision(decision_id, tenant_id)
        if decision.status == DecisionStatus.REQUIRES_APPROVAL and decision.outcome == DecisionOutcome.REQUIRE_APPROVAL:
            raise HighRiskDecisionRequiresApprovalException(f"Decision '{decision_id}' requires human approval before delegation.")

        del_plan = self.delegation.create_delegation_plan(tenant_id, decision_id, actions)
        self.decisions.update_status(decision_id, tenant_id, DecisionStatus.DELEGATED)
        self.repository.save(tenant_id, decision_id, decision)
        return del_plan

    def verify_and_finalize(self, decision_id: str, tenant_id: str) -> Decision:
        verification = self.verification.verify_decision_outcome(tenant_id, decision_id)
        self.decisions.update_status(decision_id, tenant_id, DecisionStatus.VERIFIED)

        # Build evidence bundle & finalize
        evidence_item = DecisionEvidence(
            tenant_id=tenant_id,
            decision_id=decision_id,
            evidence_type="VERIFICATION_RESULT",
            title="Outcome Verification Evidence",
            description=f"Status: {verification.status.value}",
        )
        bundle = self.evidence.create_evidence_bundle(tenant_id, decision_id, [evidence_item])
        self.evidence.finalize_bundle(bundle.bundle_id, tenant_id)

        # Finalize decision
        finalized = self.decisions.update_status(decision_id, tenant_id, DecisionStatus.FINALIZED)
        self.repository.save(tenant_id, decision_id, finalized)
        return finalized

    def list_decisions(self, tenant_id: str) -> List[Decision]:
        return self.repository.list(tenant_id)
