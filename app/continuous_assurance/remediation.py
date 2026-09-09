"""Continuous assurance remediation planner (Phase 5.54)."""

import logging
from typing import Dict, Any, List
from app.continuous_assurance.models import ContinuousAssuranceRemediationPlan
from app.continuous_assurance.delegation import ContinuousAssuranceDelegationCoordinator

logger = logging.getLogger(__name__)


class ContinuousAssuranceRemediationPlanner:
    """Plans remediation steps producing DelegationRequests for all external actions."""

    def __init__(self, delegation_coordinator: ContinuousAssuranceDelegationCoordinator) -> None:
        self.delegation_coordinator = delegation_coordinator

    def plan_remediation(
        self, tenant_id: str, drift_id: str, action_name: str
    ) -> ContinuousAssuranceRemediationPlan:
        delegation = self.delegation_coordinator.create_delegation_request(
            tenant_id=tenant_id,
            action_name=action_name,
            parameters={"drift_id": drift_id},
        )

        plan = ContinuousAssuranceRemediationPlan(
            tenant_id=tenant_id,
            drift_id=drift_id,
            steps=[{"step": 1, "type": "DELEGATION", "delegation": delegation}],
            status="PROPOSED",
        )

        logger.info(f"Planned remediation '{plan.plan_id}' for drift '{drift_id}' via delegation request")
        return plan
