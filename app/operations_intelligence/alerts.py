"""Alert Intelligence & Normalization (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEDUPLICATED = "DEDUPLICATED"
    SUPPRESSED = "SUPPRESSED"
    CORRELATED = "CORRELATED"
    CLOSED = "CLOSED"


class OperationalAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"alt_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source_system: str
    service_id: str
    alert_name: str
    fingerprint: str
    severity: AlertSeverity = AlertSeverity.HIGH
    status: AlertStatus = AlertStatus.ACTIVE
    duplicate_count: int = 1
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertManager:
    """Manages operational alert ingestion, deduplication, grouping, and suppression."""

    def __init__(self) -> None:
        self._alerts: Dict[str, OperationalAlert] = {}
        self._fingerprint_map: Dict[str, str] = {}  # (tenant_id, fingerprint) -> alert_id

    def ingest_alert(
        self,
        tenant_id: str,
        source_system: str,
        service_id: str,
        alert_name: str,
        fingerprint: str,
        severity: AlertSeverity = AlertSeverity.HIGH,
    ) -> OperationalAlert:
        fp_key = f"{tenant_id}::{fingerprint}"
        if fp_key in self._fingerprint_map:
            existing_id = self._fingerprint_map[fp_key]
            existing_alert = self._alerts[existing_id]
            existing_alert.duplicate_count += 1
            existing_alert.status = AlertStatus.DEDUPLICATED
            return existing_alert

        alert = OperationalAlert(
            tenant_id=tenant_id,
            source_system=source_system,
            service_id=service_id,
            alert_name=alert_name,
            fingerprint=fingerprint,
            severity=severity,
        )
        self._alerts[alert.alert_id] = alert
        self._fingerprint_map[fp_key] = alert.alert_id
        return alert

    def get_alert(self, tenant_id: str, alert_id: str) -> OperationalAlert:
        alert = self._alerts.get(alert_id)
        if not alert or alert.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return alert

    def list_alerts(self, tenant_id: str) -> List[OperationalAlert]:
        return [a for a in self._alerts.values() if a.tenant_id == tenant_id]
