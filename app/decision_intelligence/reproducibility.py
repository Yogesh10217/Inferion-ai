"""
Decision Reproducibility Subsystem (Addition #2).
Captures context fingerprints, evidence references, model versions, and policy evaluation results
allowing past platform decisions to be deterministically reproduced and audited.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import (
    CrossTenantDecisionIntelligenceException,
    DecisionNotFoundException,
    ImmutableDecisionRecordException,
)


class DecisionReproducibilityRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"repro_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    context_fingerprint: str
    evidence_hashes: List[str] = Field(default_factory=list)
    model_version: str = "1.0.0"
    scoring_config_version: str = "1.0.0"
    policy_evaluation_result: Dict[str, Any] = Field(default_factory=dict)
    risk_assessment_version: str = "1.0.0"
    reasoning_version: str = "1.0.0"
    reproducibility_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_reproducibility_hash(self) -> str:
        payload = {
            "record_id": self.record_id,
            "decision_id": self.decision_id,
            "tenant_id": self.tenant_id,
            "context_fingerprint": self.context_fingerprint,
            "evidence_hashes": sorted(self.evidence_hashes),
            "model_version": self.model_version,
            "scoring_config_version": self.scoring_config_version,
            "policy_evaluation_result": self.policy_evaluation_result,
            "risk_assessment_version": self.risk_assessment_version,
            "reasoning_version": self.reasoning_version,
        }
        canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(canonical_bytes).hexdigest()


class DecisionReproducibilityEngine:
    """Engine for creating, storing, and verifying decision reproducibility records."""

    def __init__(self) -> None:
        self._records: Dict[str, DecisionReproducibilityRecord] = {}

    def capture_reproducibility_record(
        self,
        decision_id: str,
        tenant_id: str,
        context_fingerprint: str,
        evidence_hashes: Optional[List[str]] = None,
        model_version: str = "1.0.0",
        scoring_config_version: str = "1.0.0",
        policy_evaluation_result: Optional[Dict[str, Any]] = None,
        risk_assessment_version: str = "1.0.0",
        reasoning_version: str = "1.0.0",
    ) -> DecisionReproducibilityRecord:
        record = DecisionReproducibilityRecord(
            decision_id=decision_id,
            tenant_id=tenant_id,
            context_fingerprint=context_fingerprint,
            evidence_hashes=evidence_hashes or [],
            model_version=model_version,
            scoring_config_version=scoring_config_version,
            policy_evaluation_result=policy_evaluation_result or {"passed": True},
            risk_assessment_version=risk_assessment_version,
            reasoning_version=reasoning_version,
        )
        record.reproducibility_hash = record.compute_reproducibility_hash()
        self._records[decision_id] = record
        return record

    def get_reproducibility_record(self, decision_id: str, tenant_id: str) -> DecisionReproducibilityRecord:
        record = self._records.get(decision_id)
        if not record:
            raise DecisionNotFoundException(f"Reproducibility record for decision '{decision_id}' not found.")
        if record.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionIntelligenceException(f"Unauthorized cross-tenant access to reproducibility record for decision '{decision_id}'")
        return record

    def verify_reproducibility(self, decision_id: str, tenant_id: str) -> bool:
        record = self.get_reproducibility_record(decision_id, tenant_id)
        expected_hash = record.compute_reproducibility_hash()
        if record.reproducibility_hash != expected_hash:
            raise ImmutableDecisionRecordException(f"Reproducibility record integrity check failed for decision '{decision_id}'")
        return True


# Also export decision_reproducibility alias
decision_reproducibility = DecisionReproducibilityEngine
