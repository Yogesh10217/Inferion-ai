"""Immutable Evidence Management for Model Intelligence (Phase 5.44)."""

import logging
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ImmutableModelIntelligenceRecordException

logger = logging.getLogger(__name__)


class ModelEvidenceIntegrity(BaseModel):
    fingerprint: str
    algorithm: str = "SHA-256"
    verified: bool = True


class ModelEvidence(BaseModel):
    evidence_id: str
    evidence_type: str
    reference_id: str
    data_ref: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelEvidenceBundle(BaseModel):
    bundle_id: str
    model_id: str
    tenant_id: str
    evidences: List[ModelEvidence] = Field(default_factory=list)
    integrity: ModelEvidenceIntegrity
    finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelEvidenceManager:
    """Manages immutable model evidence bundles with SHA-256 fingerprints and sanitized metadata."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._bundles: Dict[str, ModelEvidenceBundle] = {}

    def create_evidence_bundle(
        self,
        model_id: str,
        tenant_id: str,
        evidences: List[ModelEvidence],
    ) -> ModelEvidenceBundle:
        b_id = f"mbund-{uuid.uuid4().hex[:8]}"

        # Sanitize metadata in evidences
        sanitized_evidences = []
        for e in evidences:
            clean_meta = self.sanitizer.sanitize(e.metadata)
            sanitized_evidences.append(
                ModelEvidence(
                    evidence_id=e.evidence_id,
                    evidence_type=e.evidence_type,
                    reference_id=e.reference_id,
                    data_ref=e.data_ref,
                    metadata=clean_meta,
                    created_at=e.created_at,
                )
            )

        payload = f"{model_id}:{tenant_id}:{len(sanitized_evidences)}"
        for se in sanitized_evidences:
            payload += f":{se.evidence_id}:{se.data_ref}"

        fp = hashlib.sha256(payload.encode()).hexdigest()
        integrity = ModelEvidenceIntegrity(fingerprint=fp)

        bundle = ModelEvidenceBundle(
            bundle_id=b_id,
            model_id=model_id,
            tenant_id=tenant_id,
            evidences=sanitized_evidences,
            integrity=integrity,
            finalized=True,
        )

        self._bundles[b_id] = bundle
        logger.info(f"[MODEL EVIDENCE] Created finalized evidence bundle {b_id} (Fingerprint: {fp[:10]}...)")
        return bundle

    def get_bundle(self, bundle_id: str, tenant_id: str) -> ModelEvidenceBundle:
        b = self._bundles.get(bundle_id)
        if not b:
            raise ValueError(f"Evidence bundle '{bundle_id}' not found.")
        if b.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return b
