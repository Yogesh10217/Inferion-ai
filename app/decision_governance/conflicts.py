"""Decision conflict detection and resolution recommendation intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConflictType(str, Enum):
    POLICY = "POLICY"
    RECOMMENDATION = "RECOMMENDATION"
    PRIORITY = "PRIORITY"
    PLAN = "PLAN"
    RESOURCE = "RESOURCE"
    DEPENDENCY = "DEPENDENCY"


class ConflictSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConflictEvidence(BaseModel):
    source_a: str
    source_b: str
    description: str
    contradiction_detail: str


class ConflictResolution(BaseModel):
    recommended_action: str
    resolution_type: str = "POLICY_PREFERENCE"
    tradeoff_summary: str = ""


class DecisionConflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity = ConflictSeverity.MEDIUM
    title: str
    description: str
    evidence: List[ConflictEvidence] = Field(default_factory=list)
    resolution: Optional[ConflictResolution] = None
    is_resolved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionConflictManager:
    """Detects and resolves decision conflicts across policies, resources, and priorities."""

    def __init__(self) -> None:
        self._conflicts: Dict[str, DecisionConflict] = {}

    def create_conflict(
        self,
        tenant_id: str,
        decision_id: str,
        conflict_type: ConflictType,
        title: str,
        description: str,
        severity: ConflictSeverity = ConflictSeverity.MEDIUM,
        evidence: Optional[List[ConflictEvidence]] = None,
        resolution: Optional[ConflictResolution] = None,
    ) -> DecisionConflict:
        conflict = DecisionConflict(
            tenant_id=tenant_id,
            decision_id=decision_id,
            conflict_type=conflict_type,
            title=title,
            description=description,
            severity=severity,
            evidence=evidence or [],
            resolution=resolution,
        )
        self._conflicts[conflict.conflict_id] = conflict
        return conflict

    def list_conflicts_for_decision(self, decision_id: str, tenant_id: str) -> List[DecisionConflict]:
        return [c for c in self._conflicts.values() if c.decision_id == decision_id and c.tenant_id == tenant_id]

    def detect_conflicts(
        self,
        tenant_id: str,
        decision_id: str,
        policies: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
    ) -> List[DecisionConflict]:
        detected = []
        # Check for policy/recommendation contradiction
        if len(policies) >= 1 and len(recommendations) >= 1:
            if policies[0].get("action") != recommendations[0].get("action"):
                ev = ConflictEvidence(
                    source_a=f"Policy '{policies[0].get('name', 'P1')}'",
                    source_b=f"Recommendation '{recommendations[0].get('title', 'R1')}'",
                    description="Policy mandates DENY/REQUIRE_APPROVAL while recommendation specifies ALLOW",
                    contradiction_detail="Policy rule restriction vs recommended action mismatch",
                )
                res = ConflictResolution(
                    recommended_action="Require human approval to override policy restriction",
                    resolution_type="HUMAN_APPROVAL",
                )
                conflict = self.create_conflict(
                    tenant_id=tenant_id,
                    decision_id=decision_id,
                    conflict_type=ConflictType.POLICY,
                    title="Policy-Recommendation Conflict",
                    description="Recommended action conflicts with existing policy rule",
                    severity=ConflictSeverity.HIGH,
                    evidence=[ev],
                    resolution=res,
                )
                detected.append(conflict)
        return detected
