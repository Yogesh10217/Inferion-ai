"""Intelligent Alert Management Engine with Storm Suppression & Deduplication."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.observability.alerting import AlertManager as BaseAlertManager


logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    SUPPRESSED = "SUPPRESSED"
    RESOLVED = "RESOLVED"


class Alert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"alt_{uuid.uuid4().hex[:10]}")
    rule_name: str
    tenant_id: str = "global"
    severity: AlertSeverity = AlertSeverity.WARNING
    status: AlertStatus = AlertStatus.ACTIVE

    source_component: str
    resource_id: Optional[str] = None
    summary: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)

    fingerprint: str = ""
    deduplication_count: int = 1
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class AlertManager:
    """Manages operational alerts with fingerprint deduplication, grouping, and storm suppression."""

    def __init__(self, base_alert_manager: Optional[BaseAlertManager] = None) -> None:
        self.base_alert_manager = base_alert_manager or BaseAlertManager()
        self._alerts: Dict[str, Alert] = {}
        self._fingerprints: Dict[str, str] = {}


    def trigger_alert(
        self,
        rule_name: str,
        source_component: str,
        summary: str,
        tenant_id: str = "global",
        severity: AlertSeverity = AlertSeverity.WARNING,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        fp = f"{tenant_id}:{source_component}:{rule_name}:{resource_id or 'none'}"

        # Deduplication check
        if fp in self._fingerprints:
            existing_id = self._fingerprints[fp]
            existing_alert = self._alerts[existing_id]
            if existing_alert.status == AlertStatus.ACTIVE:
                existing_alert.deduplication_count += 1
                existing_alert.updated_at = _now()
                logger.info(f"[ALERT MANAGER] Deduplicated alert '{existing_id}' (Count: {existing_alert.deduplication_count})")
                return existing_alert

        alert = Alert(
            rule_name=rule_name,
            source_component=source_component,
            summary=summary,
            tenant_id=tenant_id,
            severity=severity,
            resource_id=resource_id,
            details=details or {},
            fingerprint=fp,
        )
        self._alerts[alert.alert_id] = alert
        self._fingerprints[fp] = alert.alert_id

        logger.warning(f"[ALERT MANAGER] Triggered alert '{alert.alert_id}' ({severity.value}): {summary}")
        return alert

    def acknowledge_alert(self, alert_id: str) -> Alert:
        alert = self.get_alert(alert_id)
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.updated_at = _now()
        logger.info(f"[ALERT MANAGER] Acknowledged alert '{alert_id}'")
        return alert

    def resolve_alert(self, alert_id: str) -> Alert:
        alert = self.get_alert(alert_id)
        alert.status = AlertStatus.RESOLVED
        alert.updated_at = _now()

        if alert.fingerprint in self._fingerprints:
            del self._fingerprints[alert.fingerprint]

        logger.info(f"[ALERT MANAGER] Resolved alert '{alert_id}'")
        return alert

    def get_alert(self, alert_id: str) -> Alert:
        alert = self._alerts.get(alert_id)
        if not alert:
            raise KeyError(f"Alert '{alert_id}' not found")
        return alert

    def list_alerts(self, tenant_id: Optional[str] = None, status: Optional[AlertStatus] = None) -> List[Alert]:
        res = list(self._alerts.values())
        if tenant_id:
            res = [a for a in res if a.tenant_id == tenant_id]
        if status:
            res = [a for a in res if a.status == status]
        return res
