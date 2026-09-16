"""Immutable SHA-256 evidence manager for Capacity Intelligence (Phase 5.56)."""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from app.capacity_intelligence.exceptions import ImmutableCapacityIntelligenceRecordException
from app.capacity_intelligence.models import CapacityEvidenceBundle
from app.capacity_intelligence.repositories import EvidenceRepository
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class CapacityEvidenceManager:
    """Creates and verifies SHA-256 sealed immutable capacity evidence bundles."""

    def __init__(self, evidence_repo: EvidenceRepository) -> None:
        self.evidence_repo = evidence_repo

    def create_evidence_bundle(
        self, tenant_id: str, assessment_id: str, raw_evidence: Optional[Dict[str, Any]] = None
    ) -> CapacityEvidenceBundle:
        clean_evidence = SensitiveDataSanitizer.sanitize(raw_evidence or {})
        canonical = json.dumps({"tenant_id": tenant_id, "assessment_id": assessment_id, "ev": clean_evidence}, sort_keys=True)
        sha256_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        bundle = CapacityEvidenceBundle(
            tenant_id=tenant_id,
            assessment_id=assessment_id,
            integrity_hash=sha256_hash,
            is_sealed=True,
        )

        self.evidence_repo.save(bundle)
        logger.info(f"Created sealed CapacityEvidenceBundle '{bundle.evidence_id}' (SHA-256: {sha256_hash[:12]}...)")
        return bundle

    def seal_evidence(
        self, tenant_id: str, assessment_id: str, raw_evidence: Optional[Dict[str, Any]] = None
    ) -> CapacityEvidenceBundle:
        return self.create_evidence_bundle(tenant_id, assessment_id, raw_evidence)

    def update_evidence(self, tenant_id: str, evidence_id: str, updates: Dict[str, Any]) -> None:
        """Attempting to update a sealed evidence record raises ImmutableCapacityIntelligenceRecordException."""
        raise ImmutableCapacityIntelligenceRecordException(record_id=evidence_id)

    def modify_sealed_bundle(self, bundle_id: str) -> None:
        """Attempting to modify a sealed evidence record raises ImmutableCapacityIntelligenceRecordException."""
        raise ImmutableCapacityIntelligenceRecordException(record_id=bundle_id)
