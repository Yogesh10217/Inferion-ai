"""Evidence Collection Orchestration Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.compliance_platform.evidence import Evidence, EvidenceManager, EvidenceSource, EvidenceType


class CollectionTriggerType(str, Enum):
    EVENT_DRIVEN = "EVENT_DRIVEN"
    SCHEDULED = "SCHEDULED"
    ON_DEMAND = "ON_DEMAND"


class EvidenceCollectionRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"evreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    idempotency_key: str
    trigger_type: CollectionTriggerType = CollectionTriggerType.ON_DEMAND
    subject_type: str
    subject_id: str
    required_evidence_types: List[EvidenceType] = Field(default_factory=list)


class EvidenceCollectionResult(BaseModel):
    request_id: str
    tenant_id: str
    collected_evidence: List[Evidence] = Field(default_factory=list)
    missing_evidence_types: List[EvidenceType] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceCollectionManager:
    """Orchestrates evidence collection from platform managers while enforcing idempotency."""

    def __init__(self, evidence_manager: EvidenceManager) -> None:
        self.evidence_manager = evidence_manager
        self._idempotency_cache: Dict[str, EvidenceCollectionResult] = {}

    def collect_evidence_for_subject(
        self,
        tenant_id: str,
        idempotency_key: str,
        subject_type: str,
        subject_id: str,
        required_types: List[EvidenceType],
    ) -> EvidenceCollectionResult:
        # Idempotency check
        if idempotency_key in self._idempotency_cache:
            return self._idempotency_cache[idempotency_key]

        collected: List[Evidence] = []
        missing: List[EvidenceType] = []

        existing_evidence = self.evidence_manager.list_evidence_for_subject(tenant_id, subject_id)
        existing_types = {e.evidence_type for e in existing_evidence}

        for req_type in required_types:
            if req_type in existing_types:
                # Add existing evidence matching type
                collected.extend([e for e in existing_evidence if e.evidence_type == req_type])
            else:
                # Synthesize/collect evidence reference from target source
                ev = self.evidence_manager.collect_evidence(
                    tenant_id=tenant_id,
                    subject_type=subject_type,
                    subject_id=subject_id,
                    evidence_type=req_type,
                    source_system=EvidenceSource.ADMINISTRATIVE_AUDIT_LEDGER,
                    source_reference=f"audit_ref_{subject_id}_{req_type.value}",
                    metadata={"collected_via": "EvidenceCollectionManager"},
                )
                collected.append(ev)

        result = EvidenceCollectionResult(
            request_id=f"evreq_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            collected_evidence=collected,
            missing_evidence_types=missing,
        )
        self._idempotency_cache[idempotency_key] = result
        return result
