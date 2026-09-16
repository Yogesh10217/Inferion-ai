"""Postmortem & Incident Review Subsystem (Phase 5.31)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.tenant import TenantIsolationValidator
from app.reliability_platform.exceptions import ImmutableReliabilityRecordException


class PostmortemStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    FINALIZED = "FINALIZED"


class PostmortemReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"pm_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    summary: str
    root_cause: str
    preventative_actions: List[str] = Field(default_factory=list)
    status: PostmortemStatus = PostmortemStatus.DRAFT
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(
                resource_id=self.report_id,
                tenant_id=self.tenant_id,
            )


class PostmortemManager:
    """Manages post-incident reports and enforces immutability on finalization."""

    def __init__(self) -> None:
        self._reports: Dict[str, PostmortemReport] = {}

    def create_postmortem(
        self,
        tenant_id: str,
        incident_id: str,
        summary: str,
        root_cause: str,
        preventative_actions: Optional[List[str]] = None,
    ) -> PostmortemReport:
        pm = PostmortemReport(
            tenant_id=tenant_id,
            incident_id=incident_id,
            summary=summary,
            root_cause=root_cause,
            preventative_actions=preventative_actions or [],
        )
        self._reports[pm.report_id] = pm
        return pm

    def finalize_postmortem(self, report_id: str, tenant_id: str) -> PostmortemReport:
        pm = self._reports.get(report_id)
        if not pm:
            raise KeyError(f"Postmortem {report_id} not found")
        TenantIsolationValidator.validate_tenant_access(tenant_id, pm.tenant_id)

        if pm.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableReliabilityRecordException(report_id)

        pm.status = PostmortemStatus.FINALIZED
        fp = FingerprintGenerator.generate(pm.model_dump(exclude={"immutable_record"}))
        ImmutableResourceValidator.finalize(pm.immutable_record, fingerprint=fp)
        return pm
