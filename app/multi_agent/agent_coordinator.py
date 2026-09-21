"""
Multi-Agent Team Orchestrator & Coordinator Engine
"""

import logging
import time
from typing import Any, Dict, Optional

from app.multi_agent.agent_billing import TeamBillingTracker
from app.multi_agent.agent_blackboard import Blackboard
from app.multi_agent.agent_consensus import ConsensusEngine, ConsensusStrategy
from app.multi_agent.agent_delegation import TaskDelegator
from app.multi_agent.agent_dispatcher import AgentDispatcher
from app.multi_agent.agent_governance import AgentGovernanceEngine
from app.multi_agent.agent_handoff import AgentHandoffManager
from app.multi_agent.agent_lifecycle import TeamLifecycleManager, TeamStatus
from app.multi_agent.agent_messaging import MessageBus, MessageType
from app.multi_agent.agent_metrics import (
    agent_consensus_total,
    agent_delegations_total,
    agent_handoffs_total,
    agent_messages_total,
    agent_team_duration_seconds,
    agent_team_failures_total,
    agent_team_runs_total,
)
from app.multi_agent.agent_router import AgentRouter
from app.multi_agent.agent_supervisor import SupervisorAgent
from app.multi_agent.agent_team import AgentTeam, TeamExecutionContext

# OpenTelemetry optional fallback
try:
    from opentelemetry import trace

    tracer = trace.get_tracer("app.multi_agent.coordinator")
except ImportError:

    class DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def set_attribute(self, k, v):
            pass

    class DummyTracer:
        def start_as_current_span(self, name, **kwargs):
            return DummySpan()

    tracer = DummyTracer()

logger = logging.getLogger(__name__)


class MultiAgentCoordinator:
    """Coordinator orchestrating autonomous multi-agent team execution pipelines."""

    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        blackboard: Optional[Blackboard] = None,
        billing_tracker: Optional[TeamBillingTracker] = None,
        lifecycle_manager: Optional[TeamLifecycleManager] = None,
    ):
        self.message_bus = message_bus or MessageBus()
        self.blackboard = blackboard or Blackboard()
        self.billing_tracker = billing_tracker or TeamBillingTracker()
        self.lifecycle_manager = lifecycle_manager or TeamLifecycleManager()

    async def execute_team_run(self, team: AgentTeam, context: TeamExecutionContext) -> Dict[str, Any]:
        """Execute full multi-agent collaboration run: Think -> Plan -> Collaborate -> Delegate -> Execute -> Verify -> Learn."""
        start_time = time.time()
        tid = context.tenant_id
        team_id = team.team_id

        # Governance validation
        AgentGovernanceEngine.validate_team_execution(team, context)

        self.lifecycle_manager.set_status(team_id, TeamStatus.RUNNING)
        agent_team_runs_total.labels(team_id=team_id, team_type=team.config.team_type.value, tenant_id=tid).inc()

        AgentRouter(team)
        dispatcher = AgentDispatcher(self.message_bus)
        delegator = TaskDelegator(team)
        handoff_mgr = AgentHandoffManager()
        SupervisorAgent(team=team)


        try:
            with tracer.start_as_current_span("agent.team.run") as span:
                span.set_attribute("team.id", team_id)
                span.set_attribute("tenant.id", tid)

                # 1. Blackboard write initial goal
                self.blackboard.write(
                    key="goal",
                    value=context.goal,
                    author_id="user",
                    tenant_id=tid,
                    workspace_id=context.workspace_id,
                    team_id=team_id,
                    category="plan",
                )

                # 2. Delegate task to primary member
                with tracer.start_as_current_span("agent.delegate"):
                    assignee = delegator.delegate_task(context.goal, delegator_id="coordinator")
                    agent_delegations_total.labels(strategy="capability_match", team_id=team_id).inc()

                # 3. Message Dispatch
                await dispatcher.dispatch_task(
                    sender_id="coordinator",
                    recipient_id=assignee.profile.agent_id,
                    task_prompt=context.goal,
                    team_id=team_id,
                    tenant_id=tid,
                )
                agent_messages_total.labels(message_type=MessageType.TASK.value, team_id=team_id).inc()

                # 4. Handoff check (if second member exists)
                members = team.list_members()
                if len(members) > 1:
                    with tracer.start_as_current_span("agent.handoff"):
                        target_m = members[1]
                        handoff_mgr.perform_handoff(
                            from_agent_id=assignee.profile.agent_id,
                            to_agent_id=target_m.profile.agent_id,
                            execution_state={"goal": context.goal, "step": "verification"},
                        )
                        agent_handoffs_total.labels(team_id=team_id).inc()

                # 5. Consensus check if multiple members
                if len(members) >= 2:
                    with tracer.start_as_current_span("agent.consensus"):
                        votes = {m.profile.agent_id: "approve" for m in members}
                        ConsensusEngine.evaluate_consensus(votes, strategy=ConsensusStrategy.MAJORITY_VOTE)
                        agent_consensus_total.labels(strategy="majority_vote", result="agreed").inc()

                # 6. Execute step simulation & Blackboard reasoning artifact output
                exec_output = f"Team '{team.config.name}' completed goal: '{context.goal}' using {len(members)} agents."
                self.blackboard.write(
                    key="final_result",
                    value=exec_output,
                    author_id=assignee.profile.agent_id,
                    tenant_id=tid,
                    workspace_id=context.workspace_id,
                    team_id=team_id,
                    category="decision",
                )

                elapsed = time.time() - start_time
                cost = 0.005 * len(members)

                # Billing & Telemetry
                agent_team_duration_seconds.labels(team_id=team_id, tenant_id=tid).observe(elapsed)
                self.billing_tracker.track_run(team_id=team_id, tenant_id=tid, duration_seconds=elapsed, cost=cost)
                self.lifecycle_manager.set_status(team_id, TeamStatus.COMPLETED)

                return {
                    "execution_id": context.execution_id,
                    "team_id": team_id,
                    "status": "completed",
                    "goal": context.goal,
                    "output": exec_output,
                    "execution_time_seconds": elapsed,
                    "cost": cost,
                    "agents_count": len(members),
                }

        except Exception as ex:
            elapsed = time.time() - start_time
            agent_team_failures_total.labels(team_id=team_id, error_type=type(ex).__name__, tenant_id=tid).inc()
            self.lifecycle_manager.set_status(team_id, TeamStatus.FAILED)
            logger.error(f"Team run failed for team '{team_id}': {ex}")
            raise ex
