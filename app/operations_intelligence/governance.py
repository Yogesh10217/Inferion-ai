"""Operational Governance Engine (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class OperationsGovernanceStatus(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class OperationsGovernanceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"req_op_{uuid.uuid4().hex[:8]}")
    code: str
    description: str
    satisfied: bool = True


class OperationsGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"gov_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action_type: str
    status: OperationsGovernanceStatus
    risk_score: float = 0.0
    reason: str
    requirements: List[OperationsGovernanceRequirement] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsGovernanceEngine:
    """Orchestrates operational governance evaluation across policy, risk, and approval requirements."""

    def __init__(self) -> None:
        self._decisions: Dict[str, OperationsGovernanceDecision] = {}

    def evaluate_governance(
        self,
        tenant_id: str,
        action_type: str,
        risk_score: float = 15.0,
        requires_approval: bool = False,
        is_blocked: bool = False,
    ) -> OperationsGovernanceDecision:
        reqs: List[OperationsGovernanceRequirement] = []

        if is_blocked:
            reqs.append(
                OperationsGovernanceRequirement(
                    code="HARD_POLICY_BLOCK", description="Hard policy violation", satisfied=False
                )
            )
            status = OperationsGovernanceStatus.BLOCK
            reason = f"Operational action '{action_type}' triggered hard policy BLOCK."
        elif requires_approval or risk_score >= 80.0:
            reqs.append(
                OperationsGovernanceRequirement(
                    code="HUMAN_APPROVAL_REQ", description="Human approval for high-risk action", satisfied=False
                )
            )
            status = OperationsGovernanceStatus.REQUIRE_APPROVAL
            reason = (
                f"High-risk operational action '{action_type}' (risk: {risk_score}) requires explicit human approval."
            )
        elif risk_score >= 60.0:
            status = OperationsGovernanceStatus.RESTRICT
            reason = f"Elevated risk score ({risk_score}) enforces RESTRICT constraints."
        elif risk_score >= 40.0:
            status = OperationsGovernanceStatus.WARN
            reason = f"Moderate risk score ({risk_score}) issues WARN status."
        else:
            status = OperationsGovernanceStatus.ALLOW
            reason = f"Operational action '{action_type}' satisfies all governance constraints."

        dec = OperationsGovernanceDecision(
            tenant_id=tenant_id,
            action_type=action_type,
            status=status,
            risk_score=risk_score,
            reason=reason,
            requirements=reqs,
        )
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, tenant_id: str, decision_id: str) -> OperationsGovernanceDecision:
        dec = self._decisions.get(decision_id)
        if not dec or dec.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return dec
