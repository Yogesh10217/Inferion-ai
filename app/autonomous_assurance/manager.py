"""Master AutonomousAssuranceManager Orchestrator Subsystem."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.autonomous_assurance.analytics import AutonomousAssuranceAnalytics
from app.autonomous_assurance.approvals import ApprovalRoutingEngine
from app.autonomous_assurance.assurance import AutonomousAssuranceEngine
from app.autonomous_assurance.billing import AutonomousAssuranceBillingTracker
from app.autonomous_assurance.boundaries import WorkflowSafetyBoundaryEngine
from app.autonomous_assurance.compensation import CompensationPlanner
from app.autonomous_assurance.concurrency import WorkflowConcurrencyManager
from app.autonomous_assurance.confidence import WorkflowConfidenceEngine
from app.autonomous_assurance.coordination import WorkflowCoordinator
from app.autonomous_assurance.delegation import AutonomousDelegationCoordinator, DelegationPlan
from app.autonomous_assurance.dependency_resolution import WorkflowDependencyResolver
from app.autonomous_assurance.evidence import AutonomousEvidenceManager
from app.autonomous_assurance.exceptions import (
    AutonomousWorkflowNotFoundException,
    ImmutableAutonomousAssuranceRecordException,
)
from app.autonomous_assurance.execution_tracking import ExecutionStatus, ExecutionTracker
from app.autonomous_assurance.explainability import WorkflowExplainabilityEngine
from app.autonomous_assurance.failure_handling import WorkflowFailureHandler
from app.autonomous_assurance.governance import AutonomousAssuranceGovernanceEngine, AutonomousGovernanceEvaluation
from app.autonomous_assurance.human_review import AutonomousHumanReviewEngine
from app.autonomous_assurance.idempotency import AutonomousIdempotencyManager
from app.autonomous_assurance.impact import WorkflowImpactEngine
from app.autonomous_assurance.learning import AutonomousWorkflowLearningEngine
from app.autonomous_assurance.limits import WorkflowLimitChecker
from app.autonomous_assurance.observability import AutonomousAssuranceMetricsCollector
from app.autonomous_assurance.orchestration import AutonomousOrchestrationEngine
from app.autonomous_assurance.planning import AutonomousPlan, AutonomousPlanner
from app.autonomous_assurance.priorities import WorkflowPriorityEngine
from app.autonomous_assurance.providers import AutonomousAssuranceProviderRegistry
from app.autonomous_assurance.recovery import RecoveryPlan, RecoveryPlanner
from app.autonomous_assurance.repositories import PlanRepository, WorkflowRepository
from app.autonomous_assurance.resilience import WorkflowResilienceEngine
from app.autonomous_assurance.risk import AutonomousWorkflowRiskEngine
from app.autonomous_assurance.rollback import RollbackPlanner
from app.autonomous_assurance.snapshots import AutonomousSnapshotStore
from app.autonomous_assurance.state_machine import WorkflowStateMachine
from app.autonomous_assurance.timeline import WorkflowTimelineEngine
from app.autonomous_assurance.trust import AutonomousWorkflowTrustEngine
from app.autonomous_assurance.verification import AutonomousVerificationEngine, VerificationResult
from app.autonomous_assurance.workflow_runtime import WorkflowRuntimeEngine
from app.autonomous_assurance.workflow_steps import WorkflowStep, WorkflowStepDependency
from app.autonomous_assurance.workflows import AutonomousWorkflow, WorkflowPriority, WorkflowStatus, WorkflowType

logger = logging.getLogger(__name__)


class AutonomousAssuranceManager:
    """Master Orchestrator unifying all Autonomous Assurance Orchestration domain engines."""

    def __init__(self, provider_registry: Optional[AutonomousAssuranceProviderRegistry] = None) -> None:
        self.provider_registry = provider_registry or AutonomousAssuranceProviderRegistry()

        self.workflow_repo = WorkflowRepository()
        self.plan_repo = PlanRepository()

        self.runtime_engine = WorkflowRuntimeEngine()
        self.orchestration_engine = AutonomousOrchestrationEngine()
        self.planner = AutonomousPlanner()
        self.coordinator = WorkflowCoordinator()
        self.dependency_resolver = WorkflowDependencyResolver()
        self.priority_engine = WorkflowPriorityEngine()
        self.state_machine = WorkflowStateMachine()

        self.concurrency_manager = WorkflowConcurrencyManager()
        self.limit_checker = WorkflowLimitChecker()
        self.boundary_engine = WorkflowSafetyBoundaryEngine()

        self.governance_engine = AutonomousAssuranceGovernanceEngine()
        self.approval_engine = ApprovalRoutingEngine()
        self.human_review_engine = AutonomousHumanReviewEngine()

        self.delegation_coordinator = AutonomousDelegationCoordinator()
        self.execution_tracker = ExecutionTracker()
        self.verification_engine = AutonomousVerificationEngine()

        self.recovery_planner = RecoveryPlanner()
        self.compensation_planner = CompensationPlanner()
        self.rollback_planner = RollbackPlanner()
        self.failure_handler = WorkflowFailureHandler()

        self.resilience_engine = WorkflowResilienceEngine()
        self.assurance_engine = AutonomousAssuranceEngine()
        self.confidence_engine = WorkflowConfidenceEngine()
        self.trust_engine = AutonomousWorkflowTrustEngine()
        self.risk_engine = AutonomousWorkflowRiskEngine()
        self.impact_engine = WorkflowImpactEngine()

        self.explainability_engine = WorkflowExplainabilityEngine()
        self.timeline_engine = WorkflowTimelineEngine()
        self.evidence_manager = AutonomousEvidenceManager()
        self.snapshot_store = AutonomousSnapshotStore()
        self.learning_engine = AutonomousWorkflowLearningEngine()

        self.analytics = AutonomousAssuranceAnalytics()
        self.metrics_collector = AutonomousAssuranceMetricsCollector()
        self.billing_tracker = AutonomousAssuranceBillingTracker()
        self.idempotency_manager = AutonomousIdempotencyManager()

        # Component Aliases
        self.workflow_manager = self
        self.step_manager = self
        self.planning_engine = self.planner
        self.boundary_evaluator = self.boundary_engine
        self.approval_manager = self.approval_engine
        self.evidence_engine = self.evidence_manager
        self.rollback_engine = self.rollback_planner
        self.delegation_manager = self.delegation_coordinator

        self._workflow_steps: Dict[str, List[WorkflowStep]] = {}

        self.planner.manager = self
        self.dependency_resolver.manager = self

        logger.info("[AUTONOMOUS ASSURANCE MASTER] Initialized master manager with all 45 domain modules.")

    def add_step(
        self,
        workflow_id: str,
        tenant_id: str,
        step_name: str,
        action_type: Any,
        target_resource: str,
        dependencies: Optional[List[str]] = None,
        auto_execute: bool = False,
    ) -> WorkflowStep:
        dep_objs = [WorkflowStepDependency(required_step_id=d) for d in (dependencies or [])]
        step = WorkflowStep(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            step_name=step_name,
            action_name=action_type.value if hasattr(action_type, "value") else str(action_type),
            target_system=target_resource,
            dependencies=dep_objs,
        )
        if workflow_id not in self._workflow_steps:
            self._workflow_steps[workflow_id] = []
        self._workflow_steps[workflow_id].append(step)
        return step

    def get_steps(self, workflow_id: str) -> List[WorkflowStep]:
        return self._workflow_steps.get(workflow_id, [])

    def run_full_autonomous_assurance_flow(
        self, tenant_id: str, name: str = "Enterprise Autonomous Assurance Flow"
    ) -> Dict[str, Any]:
        return self.run_full_autonomous_flow(tenant_id=tenant_id, title=name)

    def create_workflow(
        self,
        tenant_id: str,
        title: str,
        workflow_type: WorkflowType = WorkflowType.CROSS_DOMAIN_COORDINATION,
        description: Optional[str] = None,
        priority: WorkflowPriority = WorkflowPriority.MEDIUM,
    ) -> AutonomousWorkflow:
        wf = AutonomousWorkflow(
            tenant_id=tenant_id,
            title=title,
            workflow_type=workflow_type,
            description=description,
            priority=priority,
        )
        self.workflow_repo.save(wf)
        self.runtime_engine.init_runtime(wf.workflow_id, tenant_id)
        self.timeline_engine.add_event(wf.workflow_id, tenant_id, "WORKFLOW_CREATED", f"Workflow '{title}' created.")
        self.metrics_collector.increment("ai_autonomous_assurance_workflows_total")
        return wf

    def get_workflow(self, workflow_id: str, tenant_id: str) -> AutonomousWorkflow:
        wf = self.workflow_repo.get(workflow_id, tenant_id)
        if not wf:
            raise AutonomousWorkflowNotFoundException(f"Workflow '{workflow_id}' not found for tenant '{tenant_id}'.")
        return wf

    def create_plan(
        self, workflow_id: str, tenant_id: str, risk_score: float = 20.0, trust_score: float = 90.0
    ) -> AutonomousPlan:
        wf = self.get_workflow(workflow_id, tenant_id)

        self.state_machine.transition(
            wf, WorkflowStatus.ANALYZING, reason="Analyzing cross-domain signals and dependencies"
        )

        # Concurrency lock check
        self.concurrency_manager.acquire_lock(wf.metadata.target_resource_id, wf.workflow_id, tenant_id)

        plan = self.planner.create_plan(wf.workflow_id, tenant_id, risk_score=risk_score, trust_score=trust_score)
        self.plan_repo.save(plan)

        wf.plan_id = plan.plan_id
        self.state_machine.transition(wf, WorkflowStatus.PLANNED, reason="Plan generated")
        self.timeline_engine.add_event(wf.workflow_id, tenant_id, "PLAN_CREATED", f"Plan '{plan.plan_id}' generated.")
        return plan

    def evaluate_governance(
        self, workflow_id: str, tenant_id: str, risk_score: float = 20.0, trust_score: float = 90.0
    ) -> AutonomousGovernanceEvaluation:
        wf = self.get_workflow(workflow_id, tenant_id)

        self.state_machine.transition(wf, WorkflowStatus.GOVERNANCE_EVALUATED, reason="Evaluating governance policies")

        gov_eval = self.governance_engine.evaluate_workflow_governance(
            workflow_id, tenant_id, risk_score=risk_score, trust_score=trust_score
        )

        if gov_eval.requires_approval:
            self.state_machine.transition(wf, WorkflowStatus.REQUIRES_APPROVAL, reason="Awaiting human approval")
            self.approval_engine.create_approval_request(workflow_id, tenant_id)
            self.human_review_engine.create_ticket(workflow_id, tenant_id)
        else:
            self.state_machine.transition(wf, WorkflowStatus.APPROVED, reason="Approved autonomously within thresholds")

        return gov_eval

    def approve_workflow(
        self, workflow_id: str, tenant_id: str, approver: str, approved: bool, comments: Optional[str] = None
    ) -> AutonomousWorkflow:
        wf = self.get_workflow(workflow_id, tenant_id)
        self.approval_engine.submit_approval(workflow_id, tenant_id, approver, approved, comments)
        self.human_review_engine.resolve_ticket(workflow_id, tenant_id, approver, approved, comments)

        if approved:
            if wf.status == WorkflowStatus.REQUIRES_APPROVAL:
                self.state_machine.transition(
                    wf, WorkflowStatus.APPROVED, reason=f"Human approval granted by '{approver}'"
                )
            self.timeline_engine.add_event(wf.workflow_id, tenant_id, "WORKFLOW_APPROVED", f"Approved by '{approver}'.")
        else:
            self.state_machine.transition(wf, WorkflowStatus.DENIED, reason=f"Denied by '{approver}'")
            self.timeline_engine.add_event(wf.workflow_id, tenant_id, "WORKFLOW_DENIED", f"Denied by '{approver}'.")

        return wf

    def delegate_workflow(
        self, workflow_id: str, tenant_id: str, action_name: str = "RESTART_SERVICE"
    ) -> DelegationPlan:
        wf = self.get_workflow(workflow_id, tenant_id)
        _plan = self.planner.get_plan(workflow_id) or self.create_plan(workflow_id, tenant_id)

        is_approved = self.approval_engine.is_approved(workflow_id, tenant_id) or (wf.status == WorkflowStatus.APPROVED)

        # Enforce safety boundaries
        self.boundary_engine.evaluate_action_boundary(action_name, workflow_id, is_approved=is_approved)

        self.state_machine.transition(wf, WorkflowStatus.COORDINATING, reason="Coordinating cross-domain steps")
        self.state_machine.transition(wf, WorkflowStatus.DELEGATED, reason="Dispatching DelegationRequest")

        del_plan = self.delegation_coordinator.create_delegation_request(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            target_subsystem="OPERATIONS",
            action_type=action_name,
            is_approved=is_approved,
        )
        wf.delegation_id = del_plan.delegation_id
        self.execution_tracker.track_execution(workflow_id, tenant_id, del_plan.delegation_id)
        self.timeline_engine.add_event(
            wf.workflow_id, tenant_id, "DELEGATION_DISPATCHED", f"Delegation '{del_plan.delegation_id}' dispatched."
        )
        self.metrics_collector.increment("ai_autonomous_assurance_delegation_total")
        return del_plan

    def verify_workflow(self, workflow_id: str, tenant_id: str, simulate_failure: bool = False) -> VerificationResult:
        wf = self.get_workflow(workflow_id, tenant_id)
        del_plan = self.delegation_coordinator.get_delegation(workflow_id)
        del_id = del_plan.delegation_id if del_plan else "del_001"

        self.state_machine.transition(wf, WorkflowStatus.VERIFYING, reason="Verifying outcome")

        try:
            res = self.verification_engine.verify_workflow(
                workflow_id, tenant_id, del_id, simulate_failure=simulate_failure
            )
            wf.verification_id = res.verification_id
            self.execution_tracker.update_status(workflow_id, ExecutionStatus.SUCCEEDED, result=res.metrics_summary)
            self.timeline_engine.add_event(
                wf.workflow_id, tenant_id, "VERIFICATION_PASSED", "Verification passed cleanly."
            )
            self.metrics_collector.increment("ai_autonomous_assurance_verification_total")
            return res
        except Exception as e:
            self.execution_tracker.update_status(workflow_id, ExecutionStatus.FAILED, result={"error": str(e)})
            self.timeline_engine.add_event(
                wf.workflow_id, tenant_id, "VERIFICATION_FAILED", f"Verification failed: {e}"
            )
            raise

    def recover_workflow(
        self, workflow_id: str, tenant_id: str, failure_reason: str = "Verification failed"
    ) -> RecoveryPlan:
        wf = self.get_workflow(workflow_id, tenant_id)
        self.state_machine.transition(
            wf, WorkflowStatus.RECOVERING, reason=f"Triggering recovery due to: {failure_reason}"
        )
        rec_plan = self.recovery_planner.plan_recovery(workflow_id, tenant_id, failure_reason)
        self.timeline_engine.add_event(
            wf.workflow_id, tenant_id, "RECOVERY_PLANNED", f"Recovery planned: {failure_reason}"
        )
        self.metrics_collector.increment("ai_autonomous_assurance_recovery_total")
        return rec_plan

    def finalize_workflow(self, workflow_id: str, tenant_id: str) -> Dict[str, Any]:
        wf = self.get_workflow(workflow_id, tenant_id)
        if wf.is_finalized:
            raise ImmutableAutonomousAssuranceRecordException(
                f"Workflow '{workflow_id}' is already finalized and sealed as immutable evidence."
            )

        plan = self.planner.get_plan(workflow_id)
        del_plan = self.delegation_coordinator.get_delegation(workflow_id)
        verif = self.verification_engine.get_verification(workflow_id)

        # 1. Evidence Bundle & SHA-256 Seal
        self.evidence_manager.create_evidence_bundle(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            governance_id="gov_001",
            approval_id=workflow_id,
            delegation_id=del_plan.delegation_id if del_plan else None,
            verification_id=verif.verification_id if verif else None,
        )
        sealed_ev = self.evidence_manager.seal_evidence_bundle(workflow_id, tenant_id)
        wf.evidence_id = sealed_ev.bundle_id

        # 2. Assurance Scoring
        score = self.assurance_engine.calculate_assurance(
            workflow_id, tenant_id, verification_passed=(verif.status.value == "VERIFIED" if verif else True)
        )

        # 3. Explainability Record
        expl = self.explainability_engine.generate_explanation(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            title=wf.title,
            priority=wf.priority.value,
            risk_score=plan.risk_score if plan else 20.0,
            requires_approval=plan.requires_approval if plan else False,
        )

        # 4. Learning (Advisory auto_execute = False)
        learning = self.learning_engine.process_workflow_outcome(workflow_id, tenant_id, outcome_status="COMPLETED")

        # 5. Snapshot & Complete Workflow
        self.snapshot_store.capture_snapshot(
            workflow_id, tenant_id, status="COMPLETED", evidence_hash=sealed_ev.evidence_hash
        )
        wf.status = WorkflowStatus.COMPLETED
        wf.completed_at = datetime.now(timezone.utc)
        wf.is_finalized = True
        self.workflow_repo.save(wf)

        # Release resource lock
        self.concurrency_manager.release_lock(wf.metadata.target_resource_id, workflow_id)
        self.metrics_collector.increment("ai_autonomous_assurance_workflows_completed_total")

        wf_dict = wf.model_dump()
        wf_dict["state"] = wf.status.value

        ev_dict = sealed_ev.model_dump()
        ev_dict["evidence_sha256"] = sealed_ev.evidence_sha256

        return {
            "workflow": wf_dict,
            "plan": plan.model_dump() if plan else None,
            "delegation": del_plan.model_dump() if del_plan else None,
            "verification": verif.model_dump() if verif else None,
            "evidence": ev_dict,
            "assurance": score.model_dump(),
            "explainability": expl.model_dump(),
            "learning": learning.model_dump(),
        }

    def run_full_autonomous_flow(
        self, tenant_id: str, title: str = "Enterprise Autonomous Assurance Flow"
    ) -> Dict[str, Any]:
        """Runs end-to-end lifecycle flow: Create -> Plan -> Governance -> Approval -> Delegate -> Verify -> Evidence -> Assurance -> Complete."""
        wf = self.create_workflow(tenant_id, title)
        self.create_plan(wf.workflow_id, tenant_id, risk_score=20.0, trust_score=90.0)
        self.evaluate_governance(wf.workflow_id, tenant_id, risk_score=20.0, trust_score=90.0)
        self.approve_workflow(wf.workflow_id, tenant_id, approver="security_admin", approved=True)
        self.delegate_workflow(wf.workflow_id, tenant_id, action_name="RESTART_SERVICE")
        self.verify_workflow(wf.workflow_id, tenant_id, simulate_failure=False)
        return self.finalize_workflow(wf.workflow_id, tenant_id)

    def get_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        rep = self.analytics.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()
        return {"status": "OPERATIONAL", "report": rep.model_dump(), "metrics": metrics}
