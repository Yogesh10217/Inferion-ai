"""Continuous verification engine for Continuous Assurance (Phase 5.54)."""

import logging
import hashlib
from typing import Dict, Any
from app.continuous_assurance.models import (
    ContinuousVerificationResult,
    VerificationStatus,
)
from app.continuous_assurance.repositories import VerificationRepository

logger = logging.getLogger(__name__)


class ContinuousVerificationEngine:
    """Verifies actual runtime state hashes against expected baseline SHA-256 hashes."""

    def __init__(self, ver_repo: VerificationRepository) -> None:
        self.ver_repo = ver_repo

    def verify_resource(
        self, tenant_id: str, target_resource_id: str, expected_hash: str, actual_hash: str
    ) -> ContinuousVerificationResult:
        if expected_hash == actual_hash:
            status = VerificationStatus.VERIFIED
        else:
            status = VerificationStatus.FAILED

        ver_result = ContinuousVerificationResult(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            status=status,
            expected_hash=expected_hash,
            observed_hash=actual_hash,
            verification_details={
                "match": expected_hash == actual_hash,
                "verified_at": "ISO-8601",
            },
        )

        self.ver_repo.save(ver_result)
        logger.info(f"Verified resource '{target_resource_id}' for tenant '{tenant_id}' -> Status: {status.value}")
        return ver_result
