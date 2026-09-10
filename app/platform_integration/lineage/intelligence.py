"""Intelligence Lineage and Delegation Lineage Record Trackers (Phase 5.58)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.platform_integration.models import (
    TraceContext,
    GovernanceDecision,
    DelegationStatus,
    VerificationStatus,
)


@dataclass
class IntelligenceLineageRecord:
    lineage_id: str
    tenant_id: str
    source_platform: str
    source_signal_ids: List[str]
    derived_finding_ids: List[str]
    assessment_ids: List[str]
    trace_context: TraceContext
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DelegationLineageRecord:
    delegation_lineage_id: str
    tenant_id: str
    recommendation_id: str
    governance_decision: GovernanceDecision
    approval_id: Optional[str]
    delegation_id: str
    delegation_status: DelegationStatus
    verification_status: VerificationStatus
    trace_context: TraceContext
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
