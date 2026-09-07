"""
Autonomous Delegation Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Constructs standardized DelegationRequest objects for domain execution, enforcing
the strict invariant that Unified Intelligence ONLY delegates external mutations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget, DelegationStatus
from app.unified_intelligence.coordination import CoordinationPlan, CoordinationStep


class AutonomousDelegationEngine:
    """
    Translates unified intelligence coordination plans into standardized platform DelegationRequests.
    """
    def __init__(self):
        pass

    def create_delegation_request(
        self,
        tenant_id: str,
        plan: CoordinationPlan,
        step: CoordinationStep,
        requestor_id: str = "unified_intelligence_engine"
    ) -> DelegationRequest:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if plan.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch in delegation creation: expected {tenant_id}, got {plan.tenant_id}"
            )

        delegation_id = f"del-{uuid.uuid4().hex[:12]}"

        # Map target domain to DelegationTarget enum fallback
        target_enum = DelegationTarget.PLATFORM_OPERATIONS
        try:
            target_enum = DelegationTarget(step.target_domain.value.upper())
        except ValueError:
            target_enum = DelegationTarget.PLATFORM_OPERATIONS

        return DelegationRequest(
            delegation_id=delegation_id,
            tenant_id=tenant_id,
            target=target_enum,
            action=step.action_name,
            status=DelegationStatus.CREATED,
            payload={
                "parameters": step.parameters,
                "requires_approval": step.requires_approval,
                "requestor": requestor_id,
                "justification": f"Automated cross-domain delegation for coordination plan '{plan.title}', step '{step.step_id}'.",
                "metadata": {
                    "plan_id": plan.plan_id,
                    "step_id": step.step_id,
                    "recommendation_id": plan.recommendation_id,
                    "target_domain": step.target_domain.value
                }
            }
        )
