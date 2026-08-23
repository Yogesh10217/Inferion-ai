"""Deterministic Signal Correlation Engine."""

from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.platform_operations.signals import OperationalSignal, SignalManager
from app.platform_operations.services import ServiceCatalogManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CorrelationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"rule_{uuid.uuid4().hex[:8]}")
    name: str
    time_window_seconds: int = 300
    match_service_topology: bool = True
    match_correlation_id: bool = True
    match_trace_id: bool = True


class CorrelationCluster(BaseModel):
    cluster_id: str = Field(default_factory=lambda: f"cluster_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    primary_service_id: Optional[str] = None
    signals: List[OperationalSignal] = Field(default_factory=list)
    confidence_score: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class SignalCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    cluster_ids: List[str] = Field(default_factory=list)
    summary: str = ""
    timestamp: datetime = Field(default_factory=_now)


class CorrelationEngine:
    """Correlates operational signals deterministically with confidence and evidence."""

    def __init__(
        self,
        signal_manager: Optional[SignalManager] = None,
        service_catalog_manager: Optional[ServiceCatalogManager] = None,
    ) -> None:
        self.signal_manager = signal_manager or SignalManager()
        self.service_catalog_manager = service_catalog_manager or ServiceCatalogManager()

    def correlate_signals(
        self,
        tenant_id: str,
        time_window_minutes: int = 15,
        target_service_id: Optional[str] = None,
    ) -> List[CorrelationCluster]:
        signals = self.signal_manager.list_signals(tenant_id=tenant_id)
        if not signals:
            return []

        cutoff = _now() - timedelta(minutes=time_window_minutes)
        recent_signals = [s for s in signals if s.timestamp >= cutoff]

        clusters: List[CorrelationCluster] = []

        # Group 1: Group by explicit correlation_id or trace_id
        grouped_by_id: Dict[str, List[OperationalSignal]] = {}
        ungrouped: List[OperationalSignal] = []

        for sig in recent_signals:
            cid = sig.correlation_id or sig.trace_id
            if cid:
                grouped_by_id.setdefault(cid, []).append(sig)
            else:
                ungrouped.append(sig)

        for cid, sigs in grouped_by_id.items():
            primary_svc = sigs[0].service_id if sigs else None
            evidence = [f"Shared correlation/trace ID '{cid}' across {len(sigs)} signals."]
            clusters.append(
                CorrelationCluster(
                    tenant_id=tenant_id,
                    primary_service_id=primary_svc,
                    signals=sigs,
                    confidence_score=0.95,
                    evidence=evidence,
                )
            )

        # Group 2: Group ungrouped by service & time window
        grouped_by_service: Dict[str, List[OperationalSignal]] = {}
        for sig in ungrouped:
            if sig.service_id:
                grouped_by_service.setdefault(sig.service_id, []).append(sig)

        for svc_id, sigs in grouped_by_service.items():
            if len(sigs) >= 2:
                evidence = [f"Time-window co-occurrence ({len(sigs)} signals within {time_window_minutes}m for service '{svc_id}')."]
                clusters.append(
                    CorrelationCluster(
                        tenant_id=tenant_id,
                        primary_service_id=svc_id,
                        signals=sigs,
                        confidence_score=0.75,
                        evidence=evidence,
                    )
                )

        logger.info(f"[CORRELATION ENGINE] Correlated {len(recent_signals)} signals into {len(clusters)} clusters for tenant '{tenant_id}'")
        return clusters
