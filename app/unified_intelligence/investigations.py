"""
Unified Investigation Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Manages multi-domain investigation contexts, hypothesis tracking, evidence collection,
and lifecycle management with tenant isolation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException
)
from app.unified_intelligence.situation_awareness import EnterpriseSituation
from app.unified_intelligence.causal_analysis import CausalHypothesis


class UnifiedInvestigation:
    """
    Cross-domain investigation instance.
    """
    def __init__(
        self,
        investigation_id: str,
        tenant_id: str,
        situation_id: Optional[str],
        title: str,
        description: str,
        status: str,  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
        assigned_to: Optional[str],
        hypotheses: List[CausalHypothesis],
        evidence_ids: List[str],
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.investigation_id = investigation_id
        self.tenant_id = tenant_id
        self.situation_id = situation_id
        self.title = title
        self.description = description
        self.status = status
        self.assigned_to = assigned_to
        self.hypotheses = hypotheses
        self.evidence_ids = evidence_ids
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "investigation_id": self.investigation_id,
            "tenant_id": self.tenant_id,
            "situation_id": self.situation_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "evidence_ids": self.evidence_ids,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class UnifiedInvestigationEngine:
    """
    Orchestrates cross-domain investigation creation, updates, evidence attachment, and closure.
    """
    def __init__(self):
        pass

    def create_investigation_for_situation(
        self,
        tenant_id: str,
        situation: EnterpriseSituation,
        title: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> UnifiedInvestigation:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if situation.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch in investigation creation: expected {tenant_id}, got {situation.tenant_id}"
            )

        inv_id = f"inv-{uuid.uuid4().hex[:12]}"
        inv_title = title or f"Cross-Domain Investigation: {situation.title}"

        hypotheses: List[CausalHypothesis] = []
        if situation.causal_hypotheses:
            hypotheses = situation.causal_hypotheses

        return UnifiedInvestigation(
            investigation_id=inv_id,
            tenant_id=tenant_id,
            situation_id=situation.situation_id,
            title=inv_title,
            description=f"Investigation into situation '{situation.title}' across domains: {[d.value for d in situation.participating_domains]}.",
            status="OPEN",
            assigned_to=assigned_to,
            hypotheses=hypotheses,
            evidence_ids=situation.evidence_references
        )
