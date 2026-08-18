"""
Enterprise Multi-Agent Collaboration Subsystem Package
"""

from app.multi_agent.exceptions import (
    MultiAgentException,
    TeamNotFoundException,
    RolePermissionDenied,
    DelegationError,
    HandoffError,
    ConsensusFailedError,
    NegotiationFailedError,
    SupervisorEscalationError,
    BlackboardError,
)
from app.multi_agent.agent_role import AgentRole, RoleType
from app.multi_agent.agent_profile import AgentProfile
from app.multi_agent.agent_team import AgentTeam, TeamMember, TeamConfiguration, TeamExecutionContext, TeamType
from app.multi_agent.agent_messaging import AgentMessage, MessageBus, MessageType
from app.multi_agent.agent_router import AgentRouter, AgentRouter as MessageRouter
from app.multi_agent.agent_dispatcher import AgentDispatcher
from app.multi_agent.agent_delegation import TaskDelegator, DelegationPolicy, DelegationStrategy
from app.multi_agent.agent_handoff import AgentHandoffManager, HandoffState
from app.multi_agent.agent_consensus import ConsensusEngine, ConsensusResult, ConsensusStrategy
from app.multi_agent.agent_negotiation import NegotiationEngine, NegotiationRound, NegotiationOutcome
from app.multi_agent.agent_supervisor import SupervisorAgent
from app.multi_agent.agent_blackboard import Blackboard, BlackboardEntry
from app.multi_agent.shared_memory import SharedMemoryManager
from app.multi_agent.agent_governance import AgentGovernanceEngine
from app.multi_agent.agent_simulation import AgentSimulationEngine
from app.multi_agent.agent_lifecycle import TeamLifecycleManager, TeamStatus
from app.multi_agent.agent_metrics import (
    agent_team_runs_total,
    agent_team_failures_total,
    agent_messages_total,
    agent_delegations_total,
    agent_consensus_total,
    agent_negotiations_total,
    agent_handoffs_total,
    agent_team_duration_seconds,
)
from app.multi_agent.agent_billing import TeamBillingTracker
from app.multi_agent.agent_events import MultiAgentEventDispatcher, MultiAgentEventRegistry
from app.multi_agent.agent_coordinator import MultiAgentCoordinator

__all__ = [
    "MultiAgentException",
    "TeamNotFoundException",
    "RolePermissionDenied",
    "DelegationError",
    "HandoffError",
    "ConsensusFailedError",
    "NegotiationFailedError",
    "SupervisorEscalationError",
    "BlackboardError",
    "AgentRole",
    "RoleType",
    "AgentProfile",
    "AgentTeam",
    "TeamMember",
    "TeamConfiguration",
    "TeamExecutionContext",
    "TeamType",
    "AgentMessage",
    "MessageBus",
    "MessageRouter",
    "MessageType",
    "AgentRouter",
    "AgentDispatcher",
    "TaskDelegator",
    "DelegationPolicy",
    "DelegationStrategy",
    "AgentHandoffManager",
    "HandoffState",
    "ConsensusEngine",
    "ConsensusResult",
    "ConsensusStrategy",
    "NegotiationEngine",
    "NegotiationRound",
    "NegotiationOutcome",
    "SupervisorAgent",
    "Blackboard",
    "BlackboardEntry",
    "SharedMemoryManager",
    "AgentGovernanceEngine",
    "AgentSimulationEngine",
    "TeamLifecycleManager",
    "TeamStatus",
    "TeamBillingTracker",
    "MultiAgentEventDispatcher",
    "MultiAgentEventRegistry",
    "MultiAgentCoordinator",
]
