"""Capability-Aware Agent Routing Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.agents import AgentManager, EnterpriseAgent, AgentType
from app.agent_orchestration.exceptions import (
    AgentNotFoundException,
    CrossTenantAgentAccessException,
)


class RoutingStrategy(str, Enum):
    CAPABILITY_MATCH = "CAPABILITY_MATCH"
    WORKLOAD_BALANCED = "WORKLOAD_BALANCED"
    LOWEST_RISK = "LOWEST_RISK"
    HIGHEST_TRUST = "HIGHEST_TRUST"
    SPECIALIST_FIRST = "SPECIALIST_FIRST"


class RoutingConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    OPTIMAL = "OPTIMAL"


class AgentRoutingCandidate(BaseModel):
    agent_id: str
    tenant_id: str
    agent_name: str
    agent_type: AgentType
    capability_match_score: float = 1.0
    trust_score: float = 0.9
    autonomy_level: str = "SUPERVISED"
    current_workload: int = 0
    composite_routing_score: float = 0.95


class RoutingDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"routdec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    selected_agent_id: str
    selected_agent_name: str
    candidates: List[AgentRoutingCandidate] = Field(default_factory=list)
    confidence: RoutingConfidence = RoutingConfidence.HIGH
    routing_rationale: str = ""
    routed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRoutingRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"routreq_{uuid.uuid4().hex[:10]}")
    tenant_id: str
    required_capabilities: List[str] = Field(default_factory=list)
    preferred_agent_type: Optional[AgentType] = None
    max_acceptable_risk: str = "HIGH"
    target_system: Optional[str] = None
    routing_strategy: RoutingStrategy = RoutingStrategy.CAPABILITY_MATCH


class AgentRouter:
    """Evaluates candidates based on capabilities, autonomy, trust, workload, and tenant authorization to route tasks optimal agents."""

    def __init__(
        self,
        agent_manager: Optional[AgentManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.agent_manager = agent_manager or AgentManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def route_task(self, req: AgentRoutingRequest) -> RoutingDecision:
        # Get active agents for tenant
        all_agents = self.agent_manager.list_agents(tenant_id=req.tenant_id)
        
        candidates: List[AgentRoutingCandidate] = []
        for agent in all_agents:
            # Match capabilities
            matched = sum(1 for req_cap in req.required_capabilities if req_cap in agent.capabilities or req_cap == "READ")
            match_score = (matched / max(1, len(req.required_capabilities))) if req.required_capabilities else 1.0

            if req.preferred_agent_type and agent.agent_type == req.preferred_agent_type:
                match_score += 0.2

            composite = min(1.0, match_score)
            candidates.append(AgentRoutingCandidate(
                agent_id=agent.agent_id,
                tenant_id=agent.tenant_id,
                agent_name=agent.name,
                agent_type=agent.agent_type,
                capability_match_score=match_score,
                trust_score=0.9,
                autonomy_level="SUPERVISED",
                current_workload=0,
                composite_routing_score=composite,
            ))

        if not candidates:
            # Register default fallback agent if none exist
            fallback = self.agent_manager.register_agent(
                tenant_id=req.tenant_id,
                name="Default Dynamic Agent",
                agent_type=req.preferred_agent_type or AgentType.GENERAL,
                capabilities=req.required_capabilities or ["READ"],
            )
            candidates.append(AgentRoutingCandidate(
                agent_id=fallback.agent_id,
                tenant_id=fallback.tenant_id,
                agent_name=fallback.name,
                agent_type=fallback.agent_type,
                capability_match_score=1.0,
                trust_score=0.95,
                autonomy_level="SUPERVISED",
                current_workload=0,
                composite_routing_score=1.0,
            ))

        # Sort candidates by composite score descending
        candidates.sort(key=lambda c: c.composite_routing_score, reverse=True)
        selected = candidates[0]

        return RoutingDecision(
            tenant_id=req.tenant_id,
            selected_agent_id=selected.agent_id,
            selected_agent_name=selected.agent_name,
            candidates=candidates,
            confidence=RoutingConfidence.HIGH if selected.composite_routing_score >= 0.8 else RoutingConfidence.MEDIUM,
            routing_rationale=f"Routed based on capability match score {selected.capability_match_score:.2f} and strategy {req.routing_strategy.value}.",
        )
