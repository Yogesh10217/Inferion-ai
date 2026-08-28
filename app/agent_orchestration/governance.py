"""Agent Governance Engine Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.governance import GovernanceDecisionStatus
from app.governance import ResourceGovernanceEngine
from app.approvals import ApprovalEngine
from app.agent_orchestration.exceptions import (
    AgentPolicyViolationException,
    HighRiskAgentActionRequiresApprovalException,
    AgentExecutionBlockedException,
)


class AgentGovernanceStatus(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class AgentGovernanceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    policy_id: str = "POL_DEFAULT"
    rule_name: str
    description: str
    is_mandatory: bool = True


class AgentGovernanceEvaluation(BaseModel):
    status: AgentGovernanceStatus
    risk_score: float = 0.1
    requires_approval: bool = False
    reasons: List[str] = Field(default_factory=list)
    policy_references: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"govdec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    status: AgentGovernanceStatus
    evaluation: AgentGovernanceEvaluation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentGovernanceEngine:
    """Agent Governance Engine evaluating proposed agent actions against policies, risk thresholds, and human approval constraints."""

    def __init__(
        self,
        governance_engine: Optional[ResourceGovernanceEngine] = None,
        approval_engine: Optional[ApprovalEngine] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.governance_engine = governance_engine or ResourceGovernanceEngine()
        self.approval_engine = approval_engine or ApprovalEngine()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._decisions: Dict[str, AgentGovernanceDecision] = {}

    def evaluate_governance(
        self,
        tenant_id: str,
        agent_id: str,
        task_id: str,
        proposed_action: str,
        target_system: str = "PLATFORM_OPERATIONS",
        is_destructive: bool = False,
        estimated_cost: float = 0.0,
        risk_level: str = "LOW",
    ) -> AgentGovernanceDecision:
        reasons = []
        policy_refs = ["POL_ENTERPRISE_AGENT_SAFETY_v1"]
        status = AgentGovernanceStatus.ALLOW
        requires_approval = False
        risk_score = 0.1

        # High risk / Destructive action invariants
        if is_destructive or risk_level in ("HIGH", "CRITICAL") or "DELETE" in proposed_action.upper() or "RELEASE" in proposed_action.upper():
            status = AgentGovernanceStatus.REQUIRE_APPROVAL
            requires_approval = True
            risk_score = 0.85
            reasons.append(f"Proposed action '{proposed_action}' is destructive or high-risk ({risk_level}). Human approval required.")

        elif "MODIFY_SECURITY" in proposed_action.upper() or "GRANT_PERMISSION" in proposed_action.upper():
            status = AgentGovernanceStatus.BLOCK
            risk_score = 0.98
            reasons.append(f"Privileged security modification '{proposed_action}' is blocked for autonomous agents.")

        elif estimated_cost > 1000.0:
            status = AgentGovernanceStatus.REQUIRE_APPROVAL
            requires_approval = True
            risk_score = 0.7
            reasons.append(f"Estimated action cost ${estimated_cost:.2f} exceeds auto-approval spending limit of $1000.00.")

        else:
            reasons.append("Action evaluated and permitted under standard enterprise agent governance policy.")

        evaluation = AgentGovernanceEvaluation(
            status=status,
            risk_score=risk_score,
            requires_approval=requires_approval,
            reasons=reasons,
            policy_references=policy_refs,
        )

        decision = AgentGovernanceDecision(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task_id,
            status=status,
            evaluation=evaluation,
        )
        self._decisions[decision.decision_id] = decision

        if status == AgentGovernanceStatus.BLOCK:
            raise AgentPolicyViolationException(f"Agent action blocked: {'; '.join(reasons)}")
        elif status == AgentGovernanceStatus.REQUIRE_APPROVAL:
            raise HighRiskAgentActionRequiresApprovalException(f"Human approval required: {'; '.join(reasons)}")

        return decision
