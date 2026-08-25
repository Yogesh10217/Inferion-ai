"""AI Release Governance Subsystem (Phase 5.33)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.ai_lifecycle_platform.exceptions import ImmutableLifecycleRecordException, CrossTenantLifecycleAccessException


class ReleaseStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    CANDIDATE = "CANDIDATE"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    RELEASED = "RELEASED"
    SUSPENDED = "SUSPENDED"
    ROLLED_BACK = "ROLLED_BACK"
    RETIRED = "RETIRED"


class ReleaseRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReleaseCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: f"rc_{uuid.uuid4().hex[:12]}")
    asset_id: str
    version: str = "1.0.0"


class AIRelease(BaseModel):
    release_id: str = Field(default_factory=lambda: f"rel_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    status: ReleaseStatus = ReleaseStatus.DRAFT
    risk_level: ReleaseRisk = ReleaseRisk.MEDIUM
    candidate: ReleaseCandidate
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(resource_id=self.release_id, tenant_id=self.tenant_id)


class ReleaseManager:
    """Manages AI Releases and finalizes immutable release records."""

    def __init__(self) -> None:
        self._releases: Dict[str, AIRelease] = {}

    def create_release(
        self,
        tenant_id: str,
        title: str,
        asset_id: str,
        version: str = "1.0.0",
        risk_level: ReleaseRisk = ReleaseRisk.MEDIUM,
    ) -> AIRelease:
        cand = ReleaseCandidate(asset_id=asset_id, version=version)
        rel = AIRelease(
            tenant_id=tenant_id,
            title=title,
            risk_level=risk_level,
            candidate=cand,
        )
        self._releases[rel.release_id] = rel
        return rel

    def finalize_release(self, release_id: str, tenant_id: str) -> AIRelease:
        rel = self._releases.get(release_id)
        if not rel:
            raise KeyError(f"Release '{release_id}' not found.")
        if tenant_id != "global" and rel.tenant_id != "global" and tenant_id != rel.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, rel.tenant_id)

        if rel.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableLifecycleRecordException(release_id)

        rel.status = ReleaseStatus.RELEASED
        fp = FingerprintGenerator.generate(rel.model_dump(exclude={"immutable_record"}))
        ImmutableResourceValidator.finalize(rel.immutable_record, fingerprint=fp)
        return rel

    def get_release(self, release_id: str, tenant_id: str) -> AIRelease:
        rel = self._releases.get(release_id)
        if not rel:
            raise KeyError(f"Release '{release_id}' not found.")
        if tenant_id != "global" and rel.tenant_id != "global" and tenant_id != rel.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, rel.tenant_id)
        return rel
