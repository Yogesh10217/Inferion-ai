"""
Enterprise Multi-Agent Collaboration Subsystem Package
"""

from app.multi_agent.agent_billing import TeamBillingTracker
from app.multi_agent.agent_blackboard import Blackboard, BlackboardEntry
from app.multi_agent.agent_consensus import ConsensusEngine, ConsensusResult, ConsensusStrategy
from app.multi_agent.agent_coordinator import MultiAgentCoordinator
from app.multi_agent.agent_delegation import DelegationPolicy, DelegationStrategy, TaskDelegator
from app.multi_agent.agent_dispatcher import AgentDispatcher
from app.multi_agent.agent_events import MultiAgentEventDispatcher, MultiAgentEventRegistry
from app.multi_agent.agent_governance import AgentGovernanceEngine
from app.multi_agent.agent_handoff import AgentHandoffManager, HandoffState
from app.multi_agent.agent_lifecycle import TeamLifecycleManager, TeamStatus
from app.multi_agent.agent_messaging import AgentMessage, MessageBus, MessageType
from app.multi_agent.agent_negotiation import NegotiationEngine, NegotiationOutcome, NegotiationRound
from app.multi_agent.agent_profile import AgentProfile
from app.multi_agent.agent_role import AgentRole, RoleType
from app.multi_agent.agent_router import AgentRouter
from app.multi_agent.agent_router import AgentRouter as MessageRouter
from app.multi_agent.agent_simulation import AgentSimulationEngine
from app.multi_agent.agent_supervisor import SupervisorAgent
from app.multi_agent.agent_team import AgentTeam, TeamConfiguration, TeamExecutionContext, TeamMember, TeamType
from app.multi_agent.exceptions import (
    BlackboardError,
    ConsensusFailedError,
    DelegationError,
    HandoffError,
    MultiAgentException,
    NegotiationFailedError,
    RolePermissionDenied,
    SupervisorEscalationError,
    TeamNotFoundException,
)
from app.multi_agent.shared_memory import SharedMemoryManager

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
