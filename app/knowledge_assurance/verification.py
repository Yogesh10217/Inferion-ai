"""Knowledge Assurance Verification Module.

Provides post-delegation verification of knowledge state consistency and integrity.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeVerificationException,
)


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"


class VerificationCheck(BaseModel):
    check_id: str = Field(default_factory=lambda: f"chk-{uuid.uuid4().hex[:8]}")
    check_type: str  # REFRESH_VERIFICATION, CONFLICT_RESOLUTION_CHECK, PROVENANCE_CHECK
    target_resource_id: str
    expected_state: Dict[str, Any] = Field(default_factory=dict)
    actual_state: Dict[str, Any] = Field(default_factory=dict)
    status: VerificationStatus = VerificationStatus.PENDING
    details: str = ""


class VerificationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"vfev-{uuid.uuid4().hex[:8]}")
    source_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    hash_digest: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.hash_digest:
            raw = f"{self.evidence_id}:{self.source_type}:{str(self.payload)}"
            self.hash_digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()


class KnowledgeVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"ver-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    delegation_plan_id: Optional[str] = None
    target_resource_id: str
    status: VerificationStatus = VerificationStatus.PENDING
    checks: List[VerificationCheck] = Field(default_factory=list)
    evidence: List[VerificationEvidence] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: Optional[datetime] = None


class KnowledgeVerificationManager:
    """Manages post-delegation verification of knowledge state."""

    def __init__(self) -> None:
        self._verifications: Dict[str, KnowledgeVerification] = {}

    def initiate_verification(
        self,
        tenant_id: str,
        target_resource_id: str,
        delegation_plan_id: Optional[str] = None,
    ) -> KnowledgeVerification:
        ver = KnowledgeVerification(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            delegation_plan_id=delegation_plan_id,
        )
        self._verifications[ver.verification_id] = ver
        return ver

    def run_check(
        self,
        tenant_id: str,
        verification_id: str,
        check_type: str,
        expected_state: Dict[str, Any],
        actual_state: Dict[str, Any],
        evidence_payload: Optional[Dict[str, Any]] = None,
    ) -> VerificationCheck:
        ver = self.get_verification(tenant_id, verification_id)

        matched = expected_state == actual_state
        status = VerificationStatus.VERIFIED if matched else VerificationStatus.FAILED

        chk = VerificationCheck(
            check_type=check_type,
            target_resource_id=ver.target_resource_id,
            expected_state=expected_state,
            actual_state=actual_state,
            status=status,
            details="States match verified." if matched else "State mismatch detected.",
        )
        ver.checks.append(chk)

        if evidence_payload:
            evd = VerificationEvidence(
                source_type=check_type,
                payload=evidence_payload,
            )
            ver.evidence.append(evd)

        # Update overall status
        statuses = {c.status for c in ver.checks}
        if VerificationStatus.FAILED in statuses:
            ver.status = VerificationStatus.FAILED
        elif all(s == VerificationStatus.VERIFIED for s in statuses):
            ver.status = VerificationStatus.VERIFIED
            ver.verified_at = datetime.now(timezone.utc)
        else:
            ver.status = VerificationStatus.PARTIAL

        return chk

    def get_verification(self, tenant_id: str, verification_id: str) -> KnowledgeVerification:
        if verification_id not in self._verifications:
            raise KnowledgeVerificationException(f"Verification {verification_id} not found.")
        ver = self._verifications[verification_id]
        if ver.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return ver

    def list_verifications(self, tenant_id: str) -> List[KnowledgeVerification]:
        return [ver for ver in self._verifications.values() if ver.tenant_id == tenant_id]
