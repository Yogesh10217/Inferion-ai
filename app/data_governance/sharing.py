"""Governed Data Sharing & Cross-Tenant Sharing Authorization Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.data_governance.exceptions import DataSharingViolationException


class DataSharingScope(str, Enum):
    INTERNAL = "INTERNAL"
    CROSS_ORGANIZATION = "CROSS_ORGANIZATION"
    PARTNER = "PARTNER"
    EXTERNAL = "EXTERNAL"
    APPLICATION = "APPLICATION"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"


class DataRecipient(BaseModel):
    recipient_id: str
    recipient_tenant_id: str
    name: str
    email: Optional[str] = None
    organization_id: Optional[str] = None


class DataShareAgreement(BaseModel):
    agreement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_tenant_id: str
    target_tenant_id: str
    asset_id: str
    scope: DataSharingScope = DataSharingScope.INTERNAL
    approved: bool = False
    approved_by: Optional[str] = None
    approval_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class DataSharePolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    allow_external_sharing: bool = False
    require_approval: bool = True
    default_action: str = "DENY"


class DataShare(BaseModel):
    share_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    recipient: DataRecipient
    scope: DataSharingScope
    agreement_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataSharingManager:
    """Manages cross-tenant data sharing with strict DENY defaults."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._agreements: Dict[str, DataShareAgreement] = {}
        self._shares: Dict[str, List[DataShare]] = {}

    def request_cross_tenant_share(
        self,
        source_tenant_id: str,
        target_tenant_id: str,
        asset_id: str,
        scope: DataSharingScope = DataSharingScope.CROSS_ORGANIZATION,
        requester_id: str = "system",
    ) -> DataShareAgreement:
        if source_tenant_id == target_tenant_id:
            # Internal sharing is auto-approved
            ag = DataShareAgreement(
                source_tenant_id=source_tenant_id,
                target_tenant_id=target_tenant_id,
                asset_id=asset_id,
                scope=DataSharingScope.INTERNAL,
                approved=True,
                approved_by="auto-internal",
            )
            self._agreements[ag.agreement_id] = ag
            return ag

        # Cross-tenant sharing requires explicit approval through ApprovalEngine
        app_req = self.approval_engine.request_approval(
            execution_id=asset_id,
            action_type="CROSS_TENANT_DATA_SHARE",
            requester=requester_id,
            tenant_id=source_tenant_id,
            payload={
                "source_tenant": source_tenant_id,
                "target_tenant": target_tenant_id,
                "scope": scope.value,
            },
        )

        ag = DataShareAgreement(
            source_tenant_id=source_tenant_id,
            target_tenant_id=target_tenant_id,
            asset_id=asset_id,
            scope=scope,
            approved=False,
            approval_request_id=app_req.request_id,
        )
        self._agreements[ag.agreement_id] = ag
        return ag

    def approve_share_agreement(self, agreement_id: str, approver_id: str) -> DataShareAgreement:
        ag = self._agreements.get(agreement_id)
        if not ag:
            raise DataSharingViolationException(f"Sharing agreement '{agreement_id}' not found.")

        ag.approved = True
        ag.approved_by = approver_id
        return ag

    def validate_sharing_authorization(self, source_tenant_id: str, target_tenant_id: str, asset_id: str) -> bool:
        if source_tenant_id == target_tenant_id:
            return True

        for ag in self._agreements.values():
            if (
                ag.source_tenant_id == source_tenant_id
                and ag.target_tenant_id == target_tenant_id
                and ag.asset_id == asset_id
                and ag.approved
            ):
                return True
        return False
