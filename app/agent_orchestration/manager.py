"""Master Agent Orchestration Manager (Phase 5.36)."""

import logging
from typing import Any, Dict, List, Optional

from app.agent_orchestration.agents import AgentManager
from app.agent_orchestration.analytics import AgentAnalyticsEngine
from app.agent_orchestration.autonomy import AgentAutonomyManager
from app.agent_orchestration.billing import AgentBillingTracker, AgentCostDimension
from app.agent_orchestration.capabilities import AgentCapabilityManager, CapabilityScope
from app.agent_orchestration.collaboration import AgentCollaborationManager
from app.agent_orchestration.context import AgentContextManager
from app.agent_orchestration.coordination import AgentCoordinationManager
from app.agent_orchestration.delegation import AgentDelegationManager
from app.agent_orchestration.evidence import AgentEvidenceManager
from app.agent_orchestration.exceptions import (
    AgentAutonomyViolationException,
    HighRiskAgentActionRequiresApprovalException,
)
from app.agent_orchestration.execution import AgentExecutionManager
from app.agent_orchestration.failures import AgentFailureAnalyzer
from app.agent_orchestration.governance import AgentGovernanceEngine, AgentGovernanceStatus
from app.agent_orchestration.learning import AgentLearningManager
from app.agent_orchestration.observability import AgentMetricsCollector
from app.agent_orchestration.planning import AgentPlanningEngine
from app.agent_orchestration.recovery import AgentRecoveryManager
from app.agent_orchestration.risk import AgentRiskManager
from app.agent_orchestration.routing import AgentRouter, AgentRoutingRequest, RoutingStrategy
from app.agent_orchestration.runtime import AgentRuntimeManager
from app.agent_orchestration.safeguards import AgentSafeguardManager
from app.agent_orchestration.tasks import (
    AgentTaskManager,
    AgentTaskPriority,
    AgentTaskResult,
    AgentTaskStatus,
    AgentTaskType,
)
from app.agent_orchestration.tool_governance import AgentToolGovernanceManager
from app.agent_orchestration.traces import AgentTraceManager
from app.agent_orchestration.trust import AgentTrustEngine
from app.agent_orchestration.verification import AgentVerificationManager
from app.platform_contracts.tenant import TenantAccessGuard

logger = logging.getLogger(__name__)


class AgentOrchestrationManager:
    """Master Orchestrator for Enterprise AI Agent Lifecycle, Governance, Autonomy, Planning & Collaboration."""

    def __init__(self) -> None:
        self.tenant_guard = TenantAccessGuard()

        # Initialize internal subsystem managers
        self.agent_manager = AgentManager(tenant_guard=self.tenant_guard)
        self.capability_manager = AgentCapabilityManager(tenant_guard=self.tenant_guard)
        self.autonomy_manager = AgentAutonomyManager(tenant_guard=self.tenant_guard)
        self.task_manager = AgentTaskManager(tenant_guard=self.tenant_guard)
        self.planning_engine = AgentPlanningEngine(tenant_guard=self.tenant_guard)
        self.tool_governance_manager = AgentToolGovernanceManager(tenant_guard=self.tenant_guard)
        self.context_manager = AgentContextManager(tenant_guard=self.tenant_guard)
        self.collaboration_manager = AgentCollaborationManager(tenant_guard=self.tenant_guard)
        self.coordination_manager = AgentCoordinationManager(tenant_guard=self.tenant_guard)
        self.router = AgentRouter(agent_manager=self.agent_manager, tenant_guard=self.tenant_guard)
        self.governance_engine = AgentGovernanceEngine(tenant_guard=self.tenant_guard)
        self.delegation_manager = AgentDelegationManager(tenant_guard=self.tenant_guard)
        self.execution_manager = AgentExecutionManager(
            delegation_manager=self.delegation_manager, tenant_guard=self.tenant_guard
        )
        self.runtime_manager = AgentRuntimeManager(tenant_guard=self.tenant_guard)
        self.safeguard_manager = AgentSafeguardManager(tenant_guard=self.tenant_guard)
        self.verification_manager = AgentVerificationManager(tenant_guard=self.tenant_guard)
        self.recovery_manager = AgentRecoveryManager(
            delegation_manager=self.delegation_manager, tenant_guard=self.tenant_guard
        )
        self.failure_analyzer = AgentFailureAnalyzer(tenant_guard=self.tenant_guard)
        self.trace_manager = AgentTraceManager(tenant_guard=self.tenant_guard)
        self.evidence_manager = AgentEvidenceManager(tenant_guard=self.tenant_guard)
        self.trust_engine = AgentTrustEngine(tenant_guard=self.tenant_guard)
        self.risk_manager = AgentRiskManager(tenant_guard=self.tenant_guard)
        self.learning_manager = AgentLearningManager(tenant_guard=self.tenant_guard)
        self.analytics_engine = AgentAnalyticsEngine(tenant_guard=self.tenant_guard)
        self.metrics_collector = AgentMetricsCollector()
        self.billing_tracker = AgentBillingTracker(tenant_guard=self.tenant_guard)

        logger.info("[AGENT ORCHESTRATION] AgentOrchestrationManager initialized cleanly.")

    def run_full_agent_task_lifecycle(
        self,
        tenant_id: str,
        goal: str,
        prompt: str,
        agent_id: Optional[str] = None,
        task_type: AgentTaskType = AgentTaskType.EXECUTION,
        priority: AgentTaskPriority = AgentTaskPriority.MEDIUM,
        target_systems: Optional[List[str]] = None,
        is_destructive: bool = False,
        estimated_cost: float = 0.05,
    ) -> Dict[str, Any]:
        """Runs complete end-to-end governed agent task execution flow."""

        # 1. Routing / Agent discovery
        if not agent_id:
            route_res = self.router.route_task(
                AgentRoutingRequest(
                    tenant_id=tenant_id,
                    required_capabilities=["READ", "EXECUTE_WITH_APPROVAL"],
                    routing_strategy=RoutingStrategy.CAPABILITY_MATCH,
                )
            )
            agent_id = route_res.selected_agent_id

        agent = self.agent_manager.get_agent(agent_id, tenant_id)

        # 2. Capability Validation
        self.capability_manager.validate_agent_capabilities(
            agent_capabilities=agent.capabilities or ["READ"],
            tenant_id=tenant_id,
            required_scope=CapabilityScope.READ,
            target_system=(target_systems[0] if target_systems else None),
        )

        # 3. Task intake & Task status transition: CREATED -> VALIDATING
        task = self.task_manager.create_task(
            tenant_id=tenant_id,
            agent_id=agent_id,
            goal=goal,
            prompt=prompt,
            task_type=task_type,
            priority=priority,
            target_systems=target_systems,
        )
        self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.VALIDATING)

        # 4. Context Assembly & Knowledge Retrieval
        self.context_manager.assemble_context(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task.task_id,
            query=prompt,
            additional_data={"goal": goal},
        )

        # 5. Planning: VALIDATING -> PLANNING
        self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.PLANNING)
        plan = self.planning_engine.create_plan(
            tenant_id=tenant_id,
            task_id=task.task_id,
            agent_id=agent_id,
            goal=goal,
            target_systems=target_systems,
        )

        # 6. Autonomy Evaluation
        autonomy_policy = self.autonomy_manager.get_autonomy_policy(
            policy_id=agent.autonomy_policy_id or "default",
            tenant_id=tenant_id,
        )
        aut_eval = self.autonomy_manager.evaluate_action_autonomy(
            policy=autonomy_policy,
            proposed_action=prompt,
            target_system=(target_systems[0] if target_systems else "PLATFORM_OPERATIONS"),
            cost_dollars=estimated_cost,
        )

        if not aut_eval.is_allowed:
            self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.BLOCKED)
            self.metrics_collector.increment_autonomy_violations(tenant_id, "AUTONOMY_BOUNDARY_EXCEEDED")
            raise AgentAutonomyViolationException(aut_eval.violations[0].message)

        # 7. Governance & Risk Evaluation: PLANNING -> GOVERNANCE_PENDING
        self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.GOVERNANCE_PENDING)
        gov_dec = self.governance_engine.evaluate_governance(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task.task_id,
            proposed_action=prompt,
            is_destructive=is_destructive,
            estimated_cost=estimated_cost,
        )

        if gov_dec.status == AgentGovernanceStatus.REQUIRE_APPROVAL:
            self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.APPROVAL_PENDING)
            self.metrics_collector.increment_human_escalations(tenant_id, "HIGH_RISK_ACTION")
            raise HighRiskAgentActionRequiresApprovalException(
                "High-risk action requires human approval before proceeding."
            )

        # 8. Ready for execution: GOVERNANCE_PENDING -> READY -> EXECUTING
        self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.READY)
        self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.EXECUTING)

        # 9. Start execution session & trace
        trace = self.trace_manager.start_trace(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task.task_id,
            plan_id=plan.plan_id,
        )
        rt_sess = self.runtime_manager.create_session(
            tenant_id=tenant_id,
            agent_id=agent_id,
            execution_id=f"exec_{task.task_id}",
        )

        # Record runtime step & evaluate safeguards
        self.runtime_manager.record_step(rt_sess.session_id, tenant_id, action_name=prompt, cost=estimated_cost)
        self.safeguard_manager.evaluate_safeguards(
            tenant_id=tenant_id,
            current_steps=rt_sess.step_count,
            current_cost=rt_sess.consumed_cost,
            is_destructive=is_destructive,
        )

        # 10. Delegated Execution
        actions = [
            {"target_system": (target_systems[0] if target_systems else "PLATFORM_OPERATIONS"), "action": prompt}
        ]
        execution = self.execution_manager.start_execution(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task.task_id,
            plan_id=plan.plan_id,
            actions=actions,
        )
        self.execution_manager.complete_execution(execution.execution_id, tenant_id)

        self.trace_manager.record_step(
            trace_id=trace.trace_id,
            tenant_id=tenant_id,
            action_type="DELEGATED_EXECUTION",
            outcome_summary="Execution delegated cleanly to platform manager.",
        )

        # 11. Verification: EXECUTING -> VERIFYING
        self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.VERIFYING)
        self.verification_manager.verify_execution(
            tenant_id=tenant_id,
            execution_id=execution.execution_id,
            task_id=task.task_id,
        )

        # 12. Finalization & Trace Snapshot: VERIFYING -> COMPLETED
        final_trace = self.trace_manager.finalize_trace(trace.trace_id, tenant_id)
        evidence_bundle = self.evidence_manager.assemble_evidence_bundle(tenant_id, final_trace.trace_id)

        task_res = AgentTaskResult(
            is_successful=True,
            output_summary="Agent task executed, verified, and finalized successfully.",
            trace_id=final_trace.trace_id,
            snapshot_id=final_trace.snapshot_id,
            evidence_references=[evidence_bundle.bundle_id],
        )
        self.task_manager.transition_task_status(task.task_id, tenant_id, AgentTaskStatus.COMPLETED, result=task_res)

        # 13. Learning, Trust, Billing, Observability
        self.learning_manager.record_execution_learning(tenant_id, agent_id, execution.execution_id)
        self.trust_engine.calculate_agent_trust(tenant_id, agent_id, success_count=1)
        self.billing_tracker.record_cost(
            tenant_id, agent_id, task.task_id, AgentCostDimension.MODEL_USAGE, estimated_cost
        )
        self.metrics_collector.increment_tasks_total(tenant_id, status="COMPLETED")

        return {
            "status": "COMPLETED",
            "task": task.model_dump(),
            "plan_id": plan.plan_id,
            "execution_id": execution.execution_id,
            "trace_id": final_trace.trace_id,
            "fingerprint": final_trace.fingerprint,
            "snapshot_id": final_trace.snapshot_id,
        }

    def get_platform_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Aggregate summary of agent orchestration state."""
        agents = self.agent_manager.list_agents(tenant_id)
        tasks = self.task_manager.list_tasks(tenant_id)
        report = self.analytics_engine.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()

        return {
            "status": "OPERATIONAL",
            "tenant_id": tenant_id,
            "agent_count": len(agents),
            "task_count": len(tasks),
            "analytics": report.model_dump(),
            "metrics": metrics,
        }
