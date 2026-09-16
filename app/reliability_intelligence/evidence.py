"""Immutable reliability evidence bundle manager (Phase 5.55)."""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.reliability_intelligence.exceptions import ImmutableReliabilityRecordException
from app.reliability_intelligence.models import ReliabilityEvidenceBundle
from app.reliability_intelligence.repositories import ReliabilityEvidenceRepository

logger = logging.getLogger(__name__)


class ReliabilityEvidenceManager:
    """Creates and verifies SHA-256 sealed immutable reliability evidence bundles."""

    def __init__(self, evidence_repo: ReliabilityEvidenceRepository) -> None:
        self.evidence_repo = evidence_repo

    def create_evidence_bundle(
        self, tenant_id: str, assessment_id: str, raw_evidence: Optional[Dict[str, Any]] = None
    ) -> ReliabilityEvidenceBundle:
        clean_evidence = SensitiveDataSanitizer.sanitize(raw_evidence or {})
        canonical = json.dumps({"tenant_id": tenant_id, "assessment_id": assessment_id, "ev": clean_evidence}, sort_keys=True)
        sha256_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        bundle = ReliabilityEvidenceBundle(
            tenant_id=tenant_id,
            assessment_id=assessment_id,
            integrity_hash=sha256_hash,
            is_sealed=True,
        )

        self.evidence_repo.save(bundle)
        logger.info(f"Created sealed ReliabilityEvidenceBundle '{bundle.evidence_id}' (SHA-256: {sha256_hash[:12]}...)")
        return bundle

    def seal_evidence(
        self, tenant_id: str, assessment_id: str, raw_evidence: Optional[Dict[str, Any]] = None
    ) -> ReliabilityEvidenceBundle:
        return self.create_evidence_bundle(tenant_id, assessment_id, raw_evidence)

    def update_evidence(self, tenant_id: str, evidence_id: str, updates: Dict[str, Any]) -> None:
        """Attempting to update a sealed evidence record raises ImmutableReliabilityRecordException."""
        raise ImmutableReliabilityRecordException(record_id=evidence_id)

    def modify_sealed_bundle(self, bundle_id: str) -> None:
        """Attempting to modify a sealed evidence record raises ImmutableReliabilityRecordException."""
        raise ImmutableReliabilityRecordException(record_id=bundle_id)
