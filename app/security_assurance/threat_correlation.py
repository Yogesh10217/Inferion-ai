"""Security Threat Correlation Engine (Security-Specific)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.security_assurance.threats import SecurityThreat, SecurityThreatStore, ThreatSeverity


class CorrelatedThreatCluster(BaseModel):
    cluster_id: str = Field(default_factory=lambda: f"cluster-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    primary_threat_type: str
    overall_severity: ThreatSeverity
    threat_ids: List[str]
    summary: str
    correlated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ThreatCorrelationEngine:
    """Correlates threat intelligence signals, IOCs, and active threats into clusters."""

    def __init__(self, threat_store: SecurityThreatStore) -> None:
        self.threat_store = threat_store

    def correlate_threats(self, tenant_id: str) -> List[CorrelatedThreatCluster]:
        threats = self.threat_store.list_threats(tenant_id, status="ACTIVE")
        if not threats:
            return []

        # Group by asset or threat type
        grouped: Dict[str, List[SecurityThreat]] = {}
        for t in threats:
            key = t.target_asset_id or t.threat_type.value
            grouped.setdefault(key, []).append(t)

        clusters = []
        for key, group in grouped.items():
            if len(group) >= 1:
                severities = [g.severity for g in group]
                overall_sev = ThreatSeverity.CRITICAL if ThreatSeverity.CRITICAL in severities else ThreatSeverity.HIGH
                cluster = CorrelatedThreatCluster(
                    tenant_id=tenant_id,
                    primary_threat_type=group[0].threat_type.value,
                    overall_severity=overall_sev,
                    threat_ids=[g.threat_id for g in group],
                    summary=f"Correlated {len(group)} security threats targeting asset/type '{key}'.",
                )
                clusters.append(cluster)

        return clusters
