"""Ownership & Stewardship Governance Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.data_governance.exceptions import DataGovernanceException


class OwnershipRole(str, Enum):
    OWNER = "OWNER"
    STEWARD = "STEWARD"
    CUSTODIAN = "CUSTODIAN"
    CONSUMER = "CONSUMER"
    PROCESSOR = "PROCESSOR"
    APPROVER = "APPROVER"


class DataOwner(BaseModel):
    principal_id: str
    principal_name: str
    email: str
    department: str = "Engineering"


class DataSteward(BaseModel):
    steward_id: str
    name: str
    email: str
    domain_responsibility: str = "GENERAL"


class OwnershipAssignment(BaseModel):
    assignment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    principal_id: str
    role: OwnershipRole
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_by: str = "system"


class OwnershipManager:
    """Manages explicit asset ownership, stewardship, and governance roles."""

    def __init__(self) -> None:
        self._assignments: Dict[str, List[OwnershipAssignment]] = {}

    def assign_role(
        self,
        tenant_id: str,
        asset_id: str,
        principal_id: str,
        role: OwnershipRole,
        assigned_by: str = "system",
    ) -> OwnershipAssignment:
        assignment = OwnershipAssignment(
            tenant_id=tenant_id,
            asset_id=asset_id,
            principal_id=principal_id,
            role=role,
            assigned_by=assigned_by,
        )
        if asset_id not in self._assignments:
            self._assignments[asset_id] = []
        self._assignments[asset_id].append(assignment)
        return assignment

    def get_asset_owners(self, asset_id: str, tenant_id: str) -> List[OwnershipAssignment]:
        assignments = self._assignments.get(asset_id, [])
        return [a for a in assignments if a.tenant_id == tenant_id]

    def has_owner(self, asset_id: str, tenant_id: str) -> bool:
        assignments = self.get_asset_owners(asset_id, tenant_id)
        return any(a.role in (OwnershipRole.OWNER, OwnershipRole.STEWARD) for a in assignments)

    def validate_ownership_invariant(self, asset_id: str, tenant_id: str) -> None:
        """Enforce that critical data assets have an assigned owner or steward."""
        if not self.has_owner(asset_id, tenant_id):
            raise DataGovernanceException(
                f"Ownership Invariant Violation: Data asset '{asset_id}' must have an assigned OWNER or STEWARD.",
                tenant_id=tenant_id,
            )
