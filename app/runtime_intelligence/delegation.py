"""Runtime delegation coordinator for Runtime Intelligence (Phase 5.57)."""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RuntimeDelegationCoordinator:
    """Emits DelegationRequest structures for external action execution.

    Mandatory Invariant: Zero Direct Infrastructure Execution. Every action must produce a DelegationRequest.
    """

    def create_delegation_request(
        self,
        tenant_id: str,
        action_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        target_domain: str = "AUTONOMOUS_ASSURANCE_ORCHESTRATOR",
        risk_level: Any = "MEDIUM",
        is_approved: bool = False,
        approval_reference: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        delegation_id = f"del_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        params = parameters or {}

        # Generate deterministic idempotency key for delegation
        idemp_payload = json.dumps({"tenant": tenant_id, "action": action_name, "params": params}, sort_keys=True)
        idempotency_key = hashlib.sha256(idemp_payload.encode("utf-8")).hexdigest()

        risk_str = str(risk_level.value if hasattr(risk_level, "value") else risk_level).upper()
        requires_appr = (risk_str in ["HIGH", "CRITICAL"]) and not is_approved
        status = "PENDING_APPROVAL" if requires_appr else ("APPROVED" if is_approved else "PENDING_APPROVAL")

        delegation = {
            "delegation_id": delegation_id,
            "tenant_id": tenant_id,
            "target_domain": target_domain,
            "action_type": action_name,
            "action_name": action_name,
            "payload": params,
            "parameters": params,
            "risk_level": risk_str,
            "status": status,
            "requires_approval": requires_appr,
            "is_approved": is_approved,
            "approval_reference": approval_reference,
            "correlation_id": correlation_id or f"corr_{uuid.uuid4().hex[:8]}",
            "idempotency_key": idempotency_key,
            "execution_target": target_domain,
            "created_at": now.isoformat(),
        }
        logger.info(
            f"Created DelegationRequest '{delegation_id}' for action '{action_name}' (tenant: '{tenant_id}', status: {status}) - Zero direct mutation."
        )
        return delegation
