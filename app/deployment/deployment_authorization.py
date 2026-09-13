from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import DeploymentAuthorizationStatus
from app.deployment.secrets import SecretsSanitizer


@dataclass
class DeploymentAuthorizationRecord:
    authorization_id: str
    release_candidate_id: str
    artifact_digest: str
    git_revision: str
    environment: str
    approved_categories: List[str]
    approved_by: List[str]
    created_at: str
    expires_at: str
    status: DeploymentAuthorizationStatus
    fingerprint: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        try:
            exp_time = datetime.fromisoformat(self.expires_at)
            return datetime.now(timezone.utc) > exp_time
        except Exception:
            return True

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "authorization_id": self.authorization_id,
            "release_candidate_id": self.release_candidate_id,
            "artifact_digest": self.artifact_digest,
            "git_revision": self.git_revision,
            "environment": self.environment,
            "approved_categories": self.approved_categories,
            "approved_by": self.approved_by,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "status": self.status.value if isinstance(self.status, DeploymentAuthorizationStatus) else str(self.status),
            "fingerprint": self.fingerprint,
        })


class DeploymentAuthorizationEngine:
    """Manages multi-category deployment execution authorization with explicit TTL and binding rules."""

    REQUIRED_CATEGORIES = ["TECHNICAL", "SECURITY", "DATABASE", "OPERATIONS", "RELEASE", "DEPLOYMENT_EXECUTOR"]

    @classmethod
    def create_authorization_request(
        cls,
        release_candidate_id: str,
        artifact_digest: str,
        git_revision: str,
        environment: str = "STAGING",
        ttl_seconds: int = 3600,
    ) -> DeploymentAuthorizationRecord:
        auth_id = f"auth-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        created_at = now.isoformat()
        expires_at = datetime.fromtimestamp(now.timestamp() + ttl_seconds, tz=timezone.utc).isoformat()

        record = DeploymentAuthorizationRecord(
            authorization_id=auth_id,
            release_candidate_id=release_candidate_id,
            artifact_digest=artifact_digest,
            git_revision=git_revision,
            environment=environment,
            approved_categories=[],
            approved_by=[],
            created_at=created_at,
            expires_at=expires_at,
            status=DeploymentAuthorizationStatus.PENDING,
            fingerprint="",
        )
        record.fingerprint = cls._calculate_fingerprint(record)
        return record

    @classmethod
    def grant_category_approval(
        cls,
        record: DeploymentAuthorizationRecord,
        category: str,
        approver: str,
        current_artifact_digest: str,
        current_git_revision: str,
    ) -> DeploymentAuthorizationRecord:
        norm_cat = category.strip().upper()

        # Binding check: invalidate if artifact or git revision changed
        if current_artifact_digest != record.artifact_digest or current_git_revision != record.git_revision:
            record.status = DeploymentAuthorizationStatus.REJECTED
            record.metadata["rejection_reason"] = "DEPLOYMENT_ARTIFACT_MISMATCH: Artifact or Git revision altered since request"
            record.fingerprint = cls._calculate_fingerprint(record)
            return record

        if record.is_expired():
            record.status = DeploymentAuthorizationStatus.EXPIRED
            record.metadata["rejection_reason"] = "AUTHORIZATION_EXPIRED: Authorization request expired"
            record.fingerprint = cls._calculate_fingerprint(record)
            return record

        if norm_cat in cls.REQUIRED_CATEGORIES and norm_cat not in record.approved_categories:
            record.approved_categories.append(norm_cat)
            record.approved_by.append(f"{approver}:{norm_cat}")

        if len(record.approved_categories) >= len(cls.REQUIRED_CATEGORIES):
            record.status = DeploymentAuthorizationStatus.AUTHORIZED
        else:
            record.status = DeploymentAuthorizationStatus.PARTIALLY_APPROVED

        record.fingerprint = cls._calculate_fingerprint(record)
        return record

    @classmethod
    def validate_authorization_for_execution(
        cls,
        record: DeploymentAuthorizationRecord,
        target_artifact_digest: str,
        target_git_revision: str,
    ) -> Dict[str, Any]:
        blocking_reasons: List[str] = []

        if record.is_expired():
            record.status = DeploymentAuthorizationStatus.EXPIRED
            blocking_reasons.append("AUTHORIZATION_EXPIRED: Authorization TTL elapsed")

        if record.artifact_digest != target_artifact_digest:
            blocking_reasons.append(f"DEPLOYMENT_ARTIFACT_MISMATCH: Authorization digest '{record.artifact_digest}' != target '{target_artifact_digest}'")

        if record.git_revision != target_git_revision:
            blocking_reasons.append(f"DEPLOYMENT_ARTIFACT_MISMATCH: Authorization git rev '{record.git_revision}' != target '{target_git_revision}'")

        missing = [cat for cat in cls.REQUIRED_CATEGORIES if cat not in record.approved_categories]
        if missing:
            blocking_reasons.append(f"AUTHORIZATION_REQUIRED: Missing signoffs for categories: {missing}")

        is_valid = len(blocking_reasons) == 0 and record.status in (DeploymentAuthorizationStatus.AUTHORIZED, DeploymentAuthorizationStatus.EXECUTION_STARTED)

        return SecretsSanitizer.sanitize_structure({
            "valid": is_valid,
            "status": record.status.value if isinstance(record.status, DeploymentAuthorizationStatus) else str(record.status),
            "missing_categories": missing,
            "blocking_reasons": blocking_reasons,
            "fingerprint": record.fingerprint,
        })

    @classmethod
    def _calculate_fingerprint(cls, record: DeploymentAuthorizationRecord) -> str:
        payload = {
            "auth_id": record.authorization_id,
            "rc_id": record.release_candidate_id,
            "digest": record.artifact_digest,
            "git_rev": record.git_revision,
            "categories": sorted(record.approved_categories),
            "status": record.status.value if isinstance(record.status, DeploymentAuthorizationStatus) else str(record.status),
        }
        canonical_str = json.dumps(payload, sort_keys=True)
        return f"sha256:{hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()}"
