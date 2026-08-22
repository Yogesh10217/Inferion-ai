"""Centralized Policy Control Plane managing subsystem governance policies."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.control_plane.exceptions import PolicyViolationException

logger = logging.getLogger(__name__)


class PolicyTargetType(str, Enum):
    AGENT = "AGENT"
    AGENT_TEAM = "AGENT_TEAM"
    WORKFLOW = "WORKFLOW"
    TOOL = "TOOL"
    MCP_SERVER = "MCP_SERVER"
    MODEL = "MODEL"
    WORKER = "WORKER"
    PLAN = "PLAN"
    AUTONOMOUS_EXECUTION = "AUTONOMOUS_EXECUTION"


class ControlPlanePolicy(BaseModel):
    """Governance policy definition."""

    policy_id: str = Field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:10]}")
    name: str
    target_type: PolicyTargetType
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    rules: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    priority: int = 10
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PolicyManager:
    """Central policy engine orchestrating security rules across Agents, Workflows, Tools, and Workers."""

    def __init__(self) -> None:
        self._policies: Dict[str, ControlPlanePolicy] = {}

    def create_policy(
        self,
        name: str,
        target_type: PolicyTargetType,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None,
        priority: int = 10,
    ) -> ControlPlanePolicy:
        """Create and activate a new control plane policy."""
        policy = ControlPlanePolicy(
            name=name,
            target_type=target_type,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            rules=rules or {},
            priority=priority,
        )
        self._policies[policy.policy_id] = policy
        logger.info(f"[POLICY MANAGER] Created policy '{name}' (Target: {target_type.value}, Tenant: {tenant_id})")
        return policy

    def get_policy(self, policy_id: str) -> Optional[ControlPlanePolicy]:
        return self._policies.get(policy_id)

    def update_policy(
        self,
        policy_id: str,
        name: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
    ) -> ControlPlanePolicy:
        """Update an existing policy."""
        policy = self.get_policy(policy_id)
        if not policy:
            raise PolicyViolationException(f"Policy '{policy_id}' not found")

        if name:
            policy.name = name
        if rules:
            policy.rules = rules
        if priority is not None:
            policy.priority = priority
        policy.updated_at = datetime.now(timezone.utc)
        logger.info(f"[POLICY MANAGER] Updated policy '{policy_id}'")
        return policy

    def activate_policy(self, policy_id: str) -> ControlPlanePolicy:
        policy = self.get_policy(policy_id)
        if not policy:
            raise PolicyViolationException(f"Policy '{policy_id}' not found")
        policy.is_active = True
        policy.updated_at = datetime.now(timezone.utc)
        return policy

    def deactivate_policy(self, policy_id: str) -> ControlPlanePolicy:
        policy = self.get_policy(policy_id)
        if not policy:
            raise PolicyViolationException(f"Policy '{policy_id}' not found")
        policy.is_active = False
        policy.updated_at = datetime.now(timezone.utc)
        return policy

    def delete_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            logger.info(f"[POLICY MANAGER] Deleted policy '{policy_id}'")
            return True
        return False

    def list_policies(
        self,
        tenant_id: Optional[str] = None,
        target_type: Optional[PolicyTargetType] = None,
    ) -> List[ControlPlanePolicy]:
        """List active policies sorted by priority."""
        res = list(self._policies.values())
        if tenant_id:
            res = [p for p in res if p.tenant_id in (tenant_id, "global")]
        if target_type:
            res = [p for p in res if p.target_type == target_type]
        res.sort(key=lambda x: x.priority, reverse=True)
        return res

    def evaluate_policy(
        self,
        target_type: PolicyTargetType,
        target_id: str,
        action: str,
        tenant_id: str = "global",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Evaluate active policies against a target operation."""
        matching = self.list_policies(tenant_id=tenant_id, target_type=target_type)
        violations = []

        for pol in matching:
            if not pol.is_active:
                continue

            # Check action restriction rules
            denied_actions = pol.rules.get("deny_actions", [])
            if action in denied_actions or "*" in denied_actions:
                violations.append({
                    "policy_id": pol.policy_id,
                    "policy_name": pol.name,
                    "reason": f"Action '{action}' explicitly denied by policy '{pol.name}'",
                })

        allowed = len(violations) == 0
        if not allowed:
            logger.warning(f"[POLICY VIOLATION] Target '{target_id}' action '{action}' blocked by {len(violations)} policies")

        return {
            "allowed": allowed,
            "target_id": target_id,
            "action": action,
            "violations": violations,
        }
