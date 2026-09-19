"""Secrets Intelligence & Sensitive Non-Exposure Enforcement Engine."""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.security_assurance.exceptions import SecretsExposureException

logger = logging.getLogger(__name__)


class SecretReference(BaseModel):
    reference_id: str = Field(default_factory=lambda: f"secret-ref-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    name: str
    fingerprint: str  # SHA-256 fingerprint only
    asset_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecretsIntelligenceEngine:
    """Manages secret references strictly without storing or exposing raw secret material."""

    def __init__(self) -> None:
        self._references: Dict[str, SecretReference] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def register_secret_reference(
        self,
        tenant_id: str,
        name: str,
        raw_secret_for_hashing_only: str,
        asset_id: Optional[str] = None,
    ) -> SecretReference:
        if len(raw_secret_for_hashing_only) < 4:
            raise SecretsExposureException("Raw secret value is invalid or too short.")

        # Compute SHA-256 fingerprint immediately
        fingerprint = hashlib.sha256(raw_secret_for_hashing_only.encode("utf-8")).hexdigest()

        ref = SecretReference(
            tenant_id=tenant_id,
            name=name,
            fingerprint=fingerprint,
            asset_id=asset_id,
        )
        self._references[ref.reference_id] = ref
        logger.info(f"[SECRETS INTELLIGENCE] Registered secret reference '{name}' (fingerprint: {fingerprint[:8]}...)")
        return ref

    def list_secret_references(self, tenant_id: str) -> List[SecretReference]:
        return [r for r in self._references.values() if r.tenant_id == tenant_id]

    def scan_for_secrets(self, payload: str) -> List[str]:
        """Scans payload for potential raw secrets using sanitizer patterns."""
        sanitized = self.sanitizer.sanitize_string(payload)
        detected = []
        if (
            "[REDACTED_API_KEY]" in sanitized
            or "[REDACTED_AWS_KEY]" in sanitized
            or "[REDACTED_BEARER_TOKEN]" in sanitized
        ):
            detected.append("Potential raw credential detected in text payload.")
        return detected
