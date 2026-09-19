"""
Thread-Safe Repository Implementations for Autonomous Assurance.
Supports tenant isolation, audit trails, and data storage abstractions.
"""

import threading
from typing import Dict, List, Optional

from app.autonomous_assurance.exceptions import CrossTenantAutonomousAssuranceException
from app.autonomous_assurance.planning import AutonomousPlan
from app.autonomous_assurance.workflows import AutonomousWorkflow


class WorkflowRepository:
    """Thread-safe repository for autonomous workflows."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: Dict[str, AutonomousWorkflow] = {}

    def save(self, workflow: AutonomousWorkflow) -> AutonomousWorkflow:
        with self._lock:
            self._items[workflow.workflow_id] = workflow
            return workflow

    def get(self, workflow_id: str, tenant_id: str) -> Optional[AutonomousWorkflow]:
        with self._lock:
            item = self._items.get(workflow_id)
            if item and item.tenant_id != tenant_id and tenant_id != "global":
                raise CrossTenantAutonomousAssuranceException(
                    f"Unauthorized cross-tenant access to workflow '{workflow_id}'"
                )
            return item

    def list_by_tenant(self, tenant_id: str) -> List[AutonomousWorkflow]:
        with self._lock:
            return [w for w in self._items.values() if w.tenant_id == tenant_id or tenant_id == "global"]


class PlanRepository:
    """Thread-safe repository for autonomous plans."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: Dict[str, AutonomousPlan] = {}

    def save(self, plan: AutonomousPlan) -> AutonomousPlan:
        with self._lock:
            self._items[plan.workflow_id] = plan
            return plan

    def get(self, workflow_id: str, tenant_id: str) -> Optional[AutonomousPlan]:
        with self._lock:
            item = self._items.get(workflow_id)
            if item and item.tenant_id != tenant_id and tenant_id != "global":
                raise CrossTenantAutonomousAssuranceException(
                    f"Unauthorized cross-tenant access to plan for workflow '{workflow_id}'"
                )
            return item
