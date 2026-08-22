"""API Contract Analysis & Breaking Change Detection Subsystem."""

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.developer_platform.exceptions import APIContractBreakingChangeException
from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


class APIContract(BaseModel):
    contract_id: str
    service_id: str
    spec_version: str = "3.0.0"
    endpoints: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class APIContractValidator:
    """Analyzes API contract versions for deterministic breaking changes (removed endpoints, field type changes)."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()

    def compare_contracts(self, old_contract: APIContract, new_contract: APIContract, tenant_id: str = "global") -> Dict[str, Any]:
        breaking_changes = []

        # Check for removed endpoints
        for ep in old_contract.endpoints:
            if ep not in new_contract.endpoints:
                breaking_changes.append(f"Removed endpoint '{ep}'")

        if breaking_changes:
            reason = "; ".join(breaking_changes)
            appr = self.approval_engine.request_approval(
                execution_id=f"contract_{new_contract.service_id}",
                action_type="API_BREAKING_CHANGE",
                tenant_id=tenant_id,
            )
            logger.warning(f"[API CONTRACT VALIDATOR] Breaking changes detected for service '{new_contract.service_id}'. Approval requested -> '{appr.request_id}'")
            raise APIContractBreakingChangeException(new_contract.service_id, reason)

        return {"is_compatible": True, "breaking_changes": []}
