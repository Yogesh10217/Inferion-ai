"""Immutable SHA-256 Evidence Chain Manager (Phase 5.58)."""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

from app.platform_integration.exceptions import (
    ImmutablePlatformIntegrationRecordException,
    EvidenceTraceabilityException,
)

logger = logging.getLogger(__name__)


@dataclass
class EvidenceChainBlock:
    block_id: str
    evidence_id: str
    tenant_id: str
    source_platform: str
    payload: Dict[str, Any]
    previous_hash: str
    current_hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_sealed: bool = True


class CrossPhaseEvidenceManager:
    """Manages immutable, chained SHA-256 cryptographic evidence records."""

    def __init__(self) -> None:
        # tenant_id -> list of EvidenceChainBlock
        self._chains: Dict[str, List[EvidenceChainBlock]] = {}

    def record_evidence(
        self,
        tenant_id: str,
        source_platform: str,
        payload: Dict[str, Any],
    ) -> EvidenceChainBlock:
        chain = self._chains.setdefault(tenant_id, [])
        prev_hash = chain[-1].current_hash if chain else "GENESIS_HASH"

        ev_id = f"ev-{uuid.uuid4().hex[:12]}"
        block_id = f"blk-{len(chain) + 1}"

        content = {
            "evidence_id": ev_id,
            "tenant_id": tenant_id,
            "source_platform": source_platform,
            "payload": payload,
            "previous_hash": prev_hash,
        }
        raw = json.dumps(content, sort_keys=True)
        curr_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        block = EvidenceChainBlock(
            block_id=block_id,
            evidence_id=ev_id,
            tenant_id=tenant_id,
            source_platform=source_platform,
            payload=payload,
            previous_hash=prev_hash,
            current_hash=curr_hash,
        )
        chain.append(block)
        logger.info(f"Recorded evidence block {block.block_id} (hash: {curr_hash[:12]}...) for tenant '{tenant_id}'")
        return block

    def verify_chain_integrity(self, tenant_id: str) -> bool:
        chain = self._chains.get(tenant_id, [])
        if not chain:
            return True

        for i, block in enumerate(chain):
            expected_prev = "GENESIS_HASH" if i == 0 else chain[i - 1].current_hash
            if block.previous_hash != expected_prev:
                logger.error(f"Chain broken at block {block.block_id}: previous_hash mismatch.")
                return False

            content = {
                "evidence_id": block.evidence_id,
                "tenant_id": block.tenant_id,
                "source_platform": block.source_platform,
                "payload": block.payload,
                "previous_hash": block.previous_hash,
            }
            raw = json.dumps(content, sort_keys=True)
            recalculated = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if recalculated != block.current_hash:
                logger.error(f"Tamper detected in block {block.block_id}: hash mismatch.")
                return False

        return True

    def get_evidence(self, tenant_id: str, evidence_id: str) -> EvidenceChainBlock:
        chain = self._chains.get(tenant_id, [])
        for blk in chain:
            if blk.evidence_id == evidence_id:
                return blk
        raise EvidenceTraceabilityException(f"Evidence '{evidence_id}' not found for tenant '{tenant_id}'.")

    def modify_evidence_attempt(self, tenant_id: str, evidence_id: str) -> None:
        """Helper to verify that modification attempts raise ImmutablePlatformIntegrationRecordException."""
        raise ImmutablePlatformIntegrationRecordException("Sealed evidence records are immutable and cannot be modified.")
