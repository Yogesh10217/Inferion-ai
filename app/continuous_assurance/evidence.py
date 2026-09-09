"""Immutable evidence bundle management for Continuous Assurance (Phase 5.54)."""

import logging
import hashlib
import json
from typing import Dict, Any, List
from app.continuous_assurance.models import ContinuousAssuranceEvidenceBundle
from app.continuous_assurance.exceptions import ImmutableContinuousAssuranceRecordException
from app.continuous_assurance.repositories import EvidenceRepository
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class ContinuousAssuranceEvidenceManager:
    """Manages creation and integrity verification of SHA-256 sealed immutable evidence bundles."""

    def __init__(self, evidence_repo: EvidenceRepository) -> None:
        self.evidence_repo = evidence_repo

    def create_evidence_bundle(
        self, tenant_id: str, assessment_id: str, observation_ids: List[str]
    ) -> ContinuousAssuranceEvidenceBundle:
        clean_obs = SensitiveDataSanitizer.sanitize(observation_ids)
        canonical = json.dumps({"tenant_id": tenant_id, "assessment_id": assessment_id, "obs": clean_obs}, sort_keys=True)
        sha256_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        bundle = ContinuousAssuranceEvidenceBundle(
            tenant_id=tenant_id,
            assessment_id=assessment_id,
            observation_ids=clean_obs,
            integrity_hash=sha256_hash,
            is_sealed=True,
        )

        self.evidence_repo.save(bundle)
        logger.info(f"Created sealed ContinuousAssuranceEvidenceBundle '{bundle.evidence_id}' (SHA-256: {sha256_hash[:12]}...)")
        return bundle

    def modify_sealed_bundle(self, bundle_id: str) -> None:
        """Attempting to modify a sealed evidence record must raise ImmutableContinuousAssuranceRecordException."""
        raise ImmutableContinuousAssuranceRecordException(record_id=bundle_id)
