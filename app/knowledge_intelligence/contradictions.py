"""Knowledge Contradiction Analysis Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import CrossTenantKnowledgeAccessException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class ContradictionType(str, Enum):
    DIRECT_CONTRADICTION = "DIRECT_CONTRADICTION"
    TEMPORAL_CONTRADICTION = "TEMPORAL_CONTRADICTION"
    POLICY_CONFLICT = "POLICY_CONFLICT"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    SEMANTIC_CONFLICT = "SEMANTIC_CONFLICT"


class ContradictionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ContradictionStatus(str, Enum):
    DETECTED = "DETECTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class ContradictionEvidence(BaseModel):
    item_a_statement: str
    item_b_statement: str
    discrepancy: str


class KnowledgeContradiction(BaseModel):
    contradiction_id: str = Field(default_factory=lambda: f"kcon_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    item_a_id: str
    item_b_id: str
    contradiction_type: ContradictionType
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    status: ContradictionStatus = ContradictionStatus.DETECTED
    evidence: ContradictionEvidence
    recommendation: str = "Escalate for governance review"
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeContradictionManager:
    """Detects knowledge conflicts across sources without autonomously modifying source material."""

    def __init__(self) -> None:
        self._contradictions: Dict[str, KnowledgeContradiction] = {}

    def detect_contradiction(
        self,
        tenant_id: str,
        item_a_id: str,
        item_b_id: str,
        item_a_statement: str,
        item_b_statement: str,
        discrepancy: str,
        contradiction_type: ContradictionType = ContradictionType.DIRECT_CONTRADICTION,
        severity: ContradictionSeverity = ContradictionSeverity.MEDIUM,
    ) -> KnowledgeContradiction:
        sanitized_disc = SensitiveDataSanitizer.sanitize(discrepancy)
        ev = ContradictionEvidence(
            item_a_statement=item_a_statement,
            item_b_statement=item_b_statement,
            discrepancy=str(sanitized_disc),
        )
        rec = f"Governance review required for conflict between '{item_a_id}' and '{item_b_id}'"
        con = KnowledgeContradiction(
            tenant_id=tenant_id,
            item_a_id=item_a_id,
            item_b_id=item_b_id,
            contradiction_type=contradiction_type,
            severity=severity,
            evidence=ev,
            recommendation=rec,
        )
        self._contradictions[con.contradiction_id] = con
        return con

    def list_contradictions(self, tenant_id: str) -> List[KnowledgeContradiction]:
        return [c for c in self._contradictions.values() if c.tenant_id == tenant_id]
