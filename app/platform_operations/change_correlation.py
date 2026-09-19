"""Change Correlation & Change Intelligence Engine."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.control_plane.change_history import ChangeHistoryTracker

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OperationalChange(BaseModel):
    change_id: str = Field(default_factory=lambda: f"chg_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    change_type: str = "DEPLOYMENT"  # DEPLOYMENT, CONFIG_CHANGE, FEATURE_FLAG, POLICY_CHANGE, INTEGRATION_UPDATE
    resource_id: str
    version_or_value: str
    actor: str = "system"
    timestamp: datetime = Field(default_factory=_now)


class ChangeCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"chg_corr_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    incident_id: str
    suspected_change: OperationalChange
    correlation_time_delta_seconds: float
    confidence_score: float = 0.8
    evidence: List[str] = Field(default_factory=list)


class ChangeIntelligenceEngine:
    """Correlates deployments, feature flags, configuration changes, and policy updates with incidents."""

    def __init__(self, change_history_tracker: Optional[ChangeHistoryTracker] = None) -> None:
        self.change_history_tracker = change_history_tracker or ChangeHistoryTracker()
        self._changes: Dict[str, OperationalChange] = {}

    def record_change(
        self,
        tenant_id: str,
        change_type: str,
        resource_id: str,
        version_or_value: str,
        actor: str = "system",
    ) -> OperationalChange:
        chg = OperationalChange(
            tenant_id=tenant_id,
            change_type=change_type,
            resource_id=resource_id,
            version_or_value=version_or_value,
            actor=actor,
        )
        self._changes[chg.change_id] = chg

        # Also record in ControlPlane ChangeHistoryTracker
        try:
            self.change_history_tracker.record_change(
                resource_id=resource_id,
                resource_type=change_type,
                tenant_id=tenant_id,
                change_type="UPDATE",
                changed_by=actor,
                previous_state=None,
                new_state={"version_or_value": version_or_value},
            )
        except Exception:
            pass

        logger.info(
            f"[CHANGE INTELLIGENCE] Recorded change '{chg.change_id}' ({change_type}) for resource {resource_id}"
        )
        return chg

    def correlate_incident_with_changes(
        self,
        tenant_id: str,
        incident_id: str,
        incident_timestamp: datetime,
        service_resource_ids: List[str],
        lookback_minutes: int = 60,
    ) -> List[ChangeCorrelation]:
        correlations: List[ChangeCorrelation] = []
        cutoff = incident_timestamp - timedelta(minutes=lookback_minutes)

        tenant_changes = [
            c for c in self._changes.values() if c.tenant_id in (tenant_id, "global") and c.timestamp >= cutoff
        ]

        for chg in tenant_changes:
            if chg.resource_id in service_resource_ids or not service_resource_ids:
                delta_sec = (incident_timestamp - chg.timestamp).total_seconds()
                conf = 0.85 if abs(delta_sec) <= 300 else 0.65

                evidence = [
                    f"Change '{chg.change_id}' ({chg.change_type}) occurred {abs(delta_sec):.1f} seconds relative to incident.",
                    f"Target resource '{chg.resource_id}' updated to '{chg.version_or_value}'.",
                ]

                corr = ChangeCorrelation(
                    tenant_id=tenant_id,
                    incident_id=incident_id,
                    suspected_change=chg,
                    correlation_time_delta_seconds=delta_sec,
                    confidence_score=conf,
                    evidence=evidence,
                )
                correlations.append(corr)

        logger.info(
            f"[CHANGE INTELLIGENCE] Correlated incident '{incident_id}' with {len(correlations)} recent changes."
        )
        return correlations
