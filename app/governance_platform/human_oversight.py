"""Responsible Autonomy Boundaries & Human Oversight Specification Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AutonomyLevel(str, Enum):
    MANUAL = "MANUAL"
    ASSISTED = "ASSISTED"
    SUPERVISED = "SUPERVISED"
    CONSTRAINED_AUTONOMOUS = "CONSTRAINED_AUTONOMOUS"
    AUTONOMOUS = "AUTONOMOUS"


class OversightLevel(str, Enum):
    NONE = "NONE"
    NOTIFY = "NOTIFY"
    REVIEW = "REVIEW"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    CONTINUOUS_SUPERVISION = "CONTINUOUS_SUPERVISION"


class HumanOversightPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"ovs_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    target_resource_id: str

    autonomy_level: AutonomyLevel = AutonomyLevel.CONSTRAINED_AUTONOMOUS
    oversight_level: OversightLevel = OversightLevel.APPROVAL_REQUIRED

    allowed_tool_ids: List[str] = Field(default_factory=list)
    max_budget_per_execution: float = 100.0
    restricted_data_access_allowed: bool = False
    config_modification_allowed: bool = False

    created_at: datetime = Field(default_factory=_now)


class HumanOversightEngine:
    """Enforces autonomy boundaries and human oversight gating via ApprovalEngine."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._policies: Dict[str, HumanOversightPolicy] = {}

    def create_policy(
        self,
        name: str,
        target_resource_id: str,
        autonomy_level: AutonomyLevel = AutonomyLevel.CONSTRAINED_AUTONOMOUS,
        oversight_level: OversightLevel = OversightLevel.APPROVAL_REQUIRED,
        tenant_id: str = "global",
        restricted_data_access_allowed: bool = False,
        config_modification_allowed: bool = False,
    ) -> HumanOversightPolicy:
        pol = HumanOversightPolicy(
            name=name,
            target_resource_id=target_resource_id,
            autonomy_level=autonomy_level,
            oversight_level=oversight_level,
            tenant_id=tenant_id,
            restricted_data_access_allowed=restricted_data_access_allowed,
            config_modification_allowed=config_modification_allowed,
        )
        self._policies[pol.policy_id] = pol
        logger.info(
            f"[HUMAN OVERSIGHT] Registered policy '{pol.policy_id}' for '{target_resource_id}' ({autonomy_level.value})"
        )
        return pol

    def evaluate_action_autonomy(
        self,
        policy_id: str,
        action: str,
        is_restricted_data: bool = False,
        is_config_change: bool = False,
        cost: float = 0.0,
    ) -> Dict[str, Any]:
        pol = self.get_policy(policy_id)

        # 1. Boundary violations
        if is_restricted_data and not pol.restricted_data_access_allowed:
            req_id = f"appr_ovs_{pol.policy_id[:8]}"
            logger.warning(
                f"[HUMAN OVERSIGHT] Action '{action}' attempts restricted data access -> APPROVAL_REQUIRED ({req_id})"
            )
            return {
                "allowed": False,
                "requires_approval": True,
                "approval_request_id": req_id,
                "reason": "Restricted data access exceeds autonomy boundary",
            }

        if is_config_change and not pol.config_modification_allowed:
            req_id = f"appr_ovs_{pol.policy_id[:8]}"
            logger.warning(
                f"[HUMAN OVERSIGHT] Action '{action}' attempts config change -> APPROVAL_REQUIRED ({req_id})"
            )
            return {
                "allowed": False,
                "requires_approval": True,
                "approval_request_id": req_id,
                "reason": "Production configuration change exceeds autonomy boundary",
            }

        if cost > pol.max_budget_per_execution:
            req_id = f"appr_ovs_{pol.policy_id[:8]}"
            return {
                "allowed": False,
                "requires_approval": True,
                "approval_request_id": req_id,
                "reason": f"Execution cost ${cost:.2f} exceeds max budget ${pol.max_budget_per_execution:.2f}",
            }

        return {
            "allowed": True,
            "requires_approval": False,
            "approval_request_id": None,
            "reason": "Action complies with autonomy boundaries",
        }

    def get_policy(self, policy_id: str) -> HumanOversightPolicy:
        pol = self._policies.get(policy_id)
        if not pol:
            raise KeyError(f"Oversight policy '{policy_id}' not found")
        return pol
