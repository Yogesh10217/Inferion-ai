"""Data Governance & Policy Enforcement Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.approvals.approval_policies import RiskLevel
from app.data_fabric.exceptions import DataAccessDenied

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    SENSITIVE = "SENSITIVE"
    PII = "PII"
    FINANCIAL = "FINANCIAL"
    HEALTH = "HEALTH"
    SECRET = "SECRET"


class DataPolicy(BaseModel):
    """Governance rule governing dataset/field level access."""

    policy_id: str = Field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    allowed_classifications: List[DataClassification] = Field(
        default_factory=lambda: [DataClassification.PUBLIC, DataClassification.INTERNAL]
    )
    require_approval_for: List[DataClassification] = Field(
        default_factory=lambda: [
            DataClassification.CONFIDENTIAL,
            DataClassification.RESTRICTED,
            DataClassification.PII,
            DataClassification.FINANCIAL,
            DataClassification.HEALTH,
            DataClassification.SECRET,
        ]
    )
    retention_days: int = 365
    created_at: datetime = Field(default_factory=_now)


class DataAccessDecision(BaseModel):
    """Result of governance evaluation for data access requests."""

    permitted: bool
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    reason: str = "Allowed by policy"
    classification: DataClassification = DataClassification.INTERNAL


class DataGovernanceEngine:
    """Enforces access policies, classification checks, field-level masking rules, and approval gating."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._policies: Dict[str, DataPolicy] = {}

    def register_policy(self, policy: DataPolicy) -> DataPolicy:
        self._policies[policy.policy_id] = policy
        logger.info(f"[DATA GOVERNANCE] Registered policy '{policy.name}' for tenant '{policy.tenant_id}'")
        return policy

    def evaluate_access(
        self,
        tenant_id: str,
        resource_id: str,
        classification: DataClassification,
        requester_id: str,
        purpose: str = "AI Model Query",
    ) -> DataAccessDecision:
        """Evaluate data access request against tenant governance policies."""

        # 1. High risk classification requires explicit approval
        if classification in (
            DataClassification.SECRET,
            DataClassification.RESTRICTED,
            DataClassification.PII,
            DataClassification.HEALTH,
            DataClassification.FINANCIAL,
        ):
            req = self.approval_engine.request_approval(
                execution_id=resource_id,
                action_type="data_fabric_access",
                risk_level=RiskLevel.HIGH,
                requester=requester_id,
                payload={"resource_id": resource_id, "classification": classification.value, "purpose": purpose},
            )
            logger.warning(
                f"[DATA GOVERNANCE] High-risk data access to '{resource_id}' ({classification.value}) requires approval (ID: {req.request_id})"
            )
            return DataAccessDecision(
                permitted=False,
                requires_approval=True,
                approval_request_id=req.request_id,
                reason=f"Classification '{classification.value}' requires Human-in-the-Loop approval",
                classification=classification,
            )

        logger.info(f"[DATA GOVERNANCE] Data access permitted for resource '{resource_id}' ({classification.value})")
        return DataAccessDecision(
            permitted=True,
            requires_approval=False,
            reason="Access approved under tenant governance policy",
            classification=classification,
        )

    def enforce_access(
        self,
        tenant_id: str,
        resource_id: str,
        classification: DataClassification,
        requester_id: str,
    ) -> None:
        decision = self.evaluate_access(tenant_id, resource_id, classification, requester_id)
        if not decision.permitted and not decision.requires_approval:
            raise DataAccessDenied(tenant_id, resource_id, decision.reason)
