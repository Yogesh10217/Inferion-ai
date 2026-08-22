"""AI Agent Identity & Delegated Authorization Scope Boundary Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.identity.exceptions import AgentBoundaryViolationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AgentPermissionBoundary(BaseModel):
    boundary_id: str = Field(default_factory=lambda: f"ag_bnd_{uuid.uuid4().hex[:10]}")
    agent_id: str
    tenant_id: str = "global"

    allowed_scopes: List[str] = Field(default_factory=lambda: ["read"])
    disallowed_actions: List[str] = Field(default_factory=lambda: ["admin_override", "delete_tenant", "export_pii"])
    max_execution_budget: float = 50.0


class DelegatedAuthorization(BaseModel):
    delegation_id: str = Field(default_factory=lambda: f"del_auth_{uuid.uuid4().hex[:10]}")
    user_identity_id: str
    agent_id: str
    tenant_id: str = "global"

    delegated_scopes: List[str] = Field(default_factory=list)
    boundary: AgentPermissionBoundary = Field(default_factory=lambda: AgentPermissionBoundary(agent_id="agent_1"))
    created_at: datetime = Field(default_factory=_now)


class AgentIdentityManager:
    """Manages AI agent identity boundaries, delegated permissions, and confused deputy protections."""

    def __init__(self) -> None:
        self._delegations: Dict[str, DelegatedAuthorization] = {}

    def create_delegated_authorization(
        self,
        user_identity_id: str,
        agent_id: str,
        delegated_scopes: List[str],
        tenant_id: str = "global",
        boundary: Optional[AgentPermissionBoundary] = None,
    ) -> DelegatedAuthorization:
        del_bnd = boundary or AgentPermissionBoundary(agent_id=agent_id, tenant_id=tenant_id, allowed_scopes=delegated_scopes)

        delegation = DelegatedAuthorization(
            user_identity_id=user_identity_id,
            agent_id=agent_id,
            tenant_id=tenant_id,
            delegated_scopes=delegated_scopes,
            boundary=del_bnd,
        )
        self._delegations[delegation.delegation_id] = delegation
        logger.info(f"[AGENT IDENTITY] Delegated scopes {delegated_scopes} from '{user_identity_id}' to Agent '{agent_id}' (Tenant: {tenant_id})")
        return delegation

    def validate_agent_action(
        self,
        delegation_id: str,
        requested_action: str,
        requested_scope: str = "read",
    ) -> bool:
        del_auth = self.get_delegation(delegation_id)

        # 1. Action explicitly disallowed
        if requested_action in del_auth.boundary.disallowed_actions:
            logger.warning(f"[AGENT IDENTITY] Agent '{del_auth.agent_id}' blocked from disallowed action '{requested_action}'")
            raise AgentBoundaryViolationException(del_auth.agent_id, requested_action)

        # 2. Scope check: Requested scope must be within delegated scopes
        if requested_scope not in del_auth.delegated_scopes:
            logger.warning(f"[AGENT IDENTITY] Agent '{del_auth.agent_id}' requested scope '{requested_scope}' outside delegated boundary {del_auth.delegated_scopes}")
            raise AgentBoundaryViolationException(del_auth.agent_id, f"scope:{requested_scope}")

        return True

    def get_delegation(self, delegation_id: str) -> DelegatedAuthorization:
        del_auth = self._delegations.get(delegation_id)
        if not del_auth:
            raise KeyError(f"Delegated authorization '{delegation_id}' not found")
        return del_auth
