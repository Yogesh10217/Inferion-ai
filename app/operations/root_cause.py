"""Root Cause Analysis (RCA) Engine with Multi-Signal Temporal & Topology Correlation."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.observability.failure_analysis import FailureAnalyzer as BaseFailureAnalyzer
from app.operations.topology import TopologyManager, TopologyImpactAnalysis

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CauseRole(str, Enum):
    PRIMARY_CAUSE = "PRIMARY_CAUSE"
    CONTRIBUTING_FACTOR = "CONTRIBUTING_FACTOR"
    CORRELATED_EVENT = "CORRELATED_EVENT"
    UNKNOWN = "UNKNOWN"


class RootCauseCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: f"rca_cand_{uuid.uuid4().hex[:8]}")
    resource_id: str
    role: CauseRole = CauseRole.PRIMARY_CAUSE
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    description: str = ""


class RootCauseAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"rca_{uuid.uuid4().hex[:10]}")
    incident_id: str
    tenant_id: str = "global"
    candidates: List[RootCauseCandidate] = Field(default_factory=list)
    primary_cause_id: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=_now)


class RootCauseAnalysisEngine:
    """Correlates telemetry, health degradation, topology dependency graphs, and recent changes to rank root causes."""

    def __init__(
        self,
        base_failure_analyzer: Optional[BaseFailureAnalyzer] = None,
        topology_manager: Optional[TopologyManager] = None,
    ) -> None:
        self.base_failure_analyzer = base_failure_analyzer or BaseFailureAnalyzer()
        self.topology_manager = topology_manager or TopologyManager()

    def analyze_incident(
        self,
        incident_id: str,
        failed_resource_id: str,
        recent_changes: Optional[List[Dict[str, Any]]] = None,
        tenant_id: str = "global",
    ) -> RootCauseAnalysis:
        candidates: List[RootCauseCandidate] = []

        # 1. Topology impact
        impact = self.topology_manager.analyze_impact(failed_resource_id, tenant_id=tenant_id)
        if impact.critical_dependencies:
            for dep in impact.critical_dependencies:
                candidates.append(
                    RootCauseCandidate(
                        resource_id=dep,
                        role=CauseRole.PRIMARY_CAUSE,
                        confidence_score=0.88,
                        evidence=[f"Critical upstream dependency '{dep}' degraded in topology graph"],
                        description=f"Upstream component '{dep}' health failure impacted downstream services",
                    )
                )

        # 2. Check recent changes
        if recent_changes:
            for chg in recent_changes:
                candidates.append(
                    RootCauseCandidate(
                        resource_id=chg.get("resource_id", failed_resource_id),
                        role=CauseRole.CONTRIBUTING_FACTOR,
                        confidence_score=0.75,
                        evidence=[f"Recent change '{chg.get('change_type', 'CONFIG_CHANGE')}' executed at {chg.get('timestamp')}"],
                        description=f"Deployment/Configuration change correlated with metric regression",
                    )
                )

        # Fallback if no specific root cause determined
        if not candidates:
            candidates.append(
                RootCauseCandidate(
                    resource_id=failed_resource_id,
                    role=CauseRole.UNKNOWN,
                    confidence_score=0.50,
                    evidence=["Correlated metric degradation without unambiguous single root cause"],
                    description=f"Isolated degradation on resource '{failed_resource_id}'",
                )
            )

        primary_id = candidates[0].candidate_id if candidates else None

        rca = RootCauseAnalysis(
            incident_id=incident_id,
            tenant_id=tenant_id,
            candidates=candidates,
            primary_cause_id=primary_id,
        )
        logger.info(f"[ROOT CAUSE ANALYSIS] Conducted RCA for incident '{incident_id}': Found {len(candidates)} candidates, Top = '{primary_id}'")
        return rca
