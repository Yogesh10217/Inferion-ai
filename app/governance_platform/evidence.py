"""Automated Immutable Governance Evidence Engine."""

from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceSource(str, Enum):
    CONFIGURATION = "CONFIGURATION"
    AUDIT_LOG = "AUDIT_LOG"
    DEPLOYMENT = "DEPLOYMENT"
    APPROVAL = "APPROVAL"
    TEST_RESULT = "TEST_RESULT"
    SECURITY_SCAN = "SECURITY_SCAN"
    DATA_LINEAGE = "DATA_LINEAGE"
    MODEL_EVALUATION = "MODEL_EVALUATION"
    SLO = "SLO"
    INCIDENT = "INCIDENT"
    FINOPS = "FINOPS"
    ACCESS_LOG = "ACCESS_LOG"
    POLICY_DECISION = "POLICY_DECISION"


class EvidenceType(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"
    EXTERNAL = "EXTERNAL"


class Evidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"evd_{uuid.uuid4().hex[:10]}")
    source_system: EvidenceSource = EvidenceSource.AUDIT_LOG
    evidence_type: EvidenceType = EvidenceType.AUTOMATIC
    source_record_id: str = ""
    tenant_id: str = "global"
    resource_id: str = ""

    payload: Dict[str, Any] = Field(default_factory=dict)
    collected_at: datetime = Field(default_factory=_now)

    content_hash: str = ""
    previous_hash: Optional[str] = None


class EvidenceCollector:
    """Collects and registers immutable, integrity-hashed evidence from platform subsystems."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._evidence_store: Dict[str, Evidence] = {}
        self._last_hash: Optional[str] = None

    def collect_evidence(
        self,
        source_system: EvidenceSource,
        source_record_id: str,
        resource_id: str,
        payload: Dict[str, Any],
        tenant_id: str = "global",
        evidence_type: EvidenceType = EvidenceType.AUTOMATIC,
    ) -> Evidence:
        # Sanitize payload strings
        sanitized_payload = self._sanitize_dict(payload)

        # Compute deterministic content SHA-256 hash
        payload_str = json.dumps(sanitized_payload, sort_keys=True, default=str)
        content_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        evd = Evidence(
            source_system=source_system,
            evidence_type=evidence_type,
            source_record_id=source_record_id,
            tenant_id=tenant_id,
            resource_id=resource_id,
            payload=sanitized_payload,
            content_hash=content_hash,
            previous_hash=self._last_hash,
        )

        self._evidence_store[evd.evidence_id] = evd
        self._last_hash = content_hash
        logger.info(f"[EVIDENCE COLLECTOR] Registered evidence '{evd.evidence_id}' from {source_system.value} (Hash: {content_hash[:8]})")
        return evd

    def get_evidence(self, evidence_id: str) -> Evidence:
        evd = self._evidence_store.get(evidence_id)
        if not evd:
            raise KeyError(f"Evidence record '{evidence_id}' not found")
        return evd

    def list_evidence(self, tenant_id: Optional[str] = None, resource_id: Optional[str] = None) -> List[Evidence]:
        res = list(self._evidence_store.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        if resource_id:
            res = [r for r in res if r.resource_id == resource_id]
        return res

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in data.items():
            if isinstance(v, str):
                sanitized[k] = self.secret_manager.sanitize_text(v) if hasattr(self.secret_manager, "sanitize_text") else v
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized
