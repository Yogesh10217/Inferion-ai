"""Agent Integration Adapter & Delegated Scope Boundary Enforcement."""

import logging
from typing import Dict, Any, Optional

from app.identity.agent_identity import AgentIdentityManager
from app.identity.exceptions import AgentBoundaryViolationException

logger = logging.getLogger(__name__)


class AgentIntegrationAdapter:
    """Adapts agent external integration requests while enforcing agent delegated scope boundaries."""

    def __init__(self, agent_identity_manager: Optional[AgentIdentityManager] = None) -> None:
        self.agent_identity_manager = agent_identity_manager or AgentIdentityManager()

    def execute_external_action_for_agent(
        self,
        agent_id: str,
        integration_name: str,
        action: str,
        delegation_id: Optional[str] = None,
        tenant_id: str = "global",
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Validate delegation boundary
        if delegation_id:
            req_scope = "write" if ("delete" in action or "create" in action or "write" in action) else "read"
            self.agent_identity_manager.validate_agent_action(
                delegation_id=delegation_id,
                requested_action=action,
                requested_scope=req_scope,
            )

        logger.info(f"[AGENT INTEGRATION ADAPTER] Agent '{agent_id}' executed action '{action}' on integration '{integration_name}'")
        return {"status": "SUCCESS", "agent_id": agent_id, "integration": integration_name, "action": action}
