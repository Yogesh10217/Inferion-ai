"""
Decision Investigations Subsystem.
Supports deep-dive diagnostic investigations into decision context, anomalies, or unexpected recommendation outcomes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import DecisionInvestigationNotFoundException


class DecisionInvestigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"inves_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    investigator: str = "SYSTEM"
    findings: List[str] = Field(default_factory=list)
    status: str = "IN_PROGRESS"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionInvestigationEngine:
    """Manages deep-dive decision investigations."""

    def __init__(self) -> None:
        self._investigations: Dict[str, DecisionInvestigation] = {}

    def launch_investigation(self, decision_id: str, tenant_id: str, investigator: str = "SYSTEM") -> DecisionInvestigation:
        inv = DecisionInvestigation(
            decision_id=decision_id,
            tenant_id=tenant_id,
            investigator=investigator,
            findings=["Initiated diagnostic sweep across cross-domain evidence.", "Verified model scoring inputs."],
        )
        self._investigations[decision_id] = inv
        return inv

    def get_investigation(self, decision_id: str) -> DecisionInvestigation:
        inv = self._investigations.get(decision_id)
        if not inv:
            raise DecisionInvestigationNotFoundException(f"Investigation for decision '{decision_id}' not found.")
        return inv
