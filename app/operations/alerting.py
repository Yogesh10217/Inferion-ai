"""
Alert Engine & Alert Management Module for Phase 5.68 and legacy operations support.
Generates alerts from SLO breaches, error budget exhaustions, anomalies, and health failures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.deployment.secrets import SecretsSanitizer
from app.observability.alerting import AlertManager as BaseAlertManager
from app.operations.anomaly_detection import Anomaly, AnomalySeverity
from app.operations.error_budget import ErrorBudgetResult, ErrorBudgetStatus
from app.operations.slo import SLOResult, SLOStatus

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertStatus(str, Enum):
    OPEN = "OPEN"
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    SUPPRESSED = "SUPPRESSED"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


@dataclass
class Alert:
    alert_id: str
    source: str
    alert_type: str
    service: str
    severity: AlertSeverity
    status: AlertStatus
    summary: str
    timestamp: str
    deployment_identity: str
    details: Dict[str, Any] = field(default_factory=dict)
    occurrence_count: int = 1
    fingerprint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "source": self.source,
            "alert_type": self.alert_type,
            "service": self.service,
            "severity": self.severity.value,
            "status": self.status.value,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "timestamp": self.timestamp,
            "deployment_identity": self.deployment_identity,
            "details": SecretsSanitizer.sanitize_structure(self.details),
            "occurrence_count": self.occurrence_count,
            "fingerprint": self.fingerprint,
        }


class LegacyAlert(BaseModel):
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


class AlertEngine:
    """Generates structured operational alerts from platform observations and evaluations."""

    def __init__(self, service_name: str = "enterprise-ai-platform") -> None:
        self.service_name = service_name

    def generate_alerts(
        self,
        slo_results: List[SLOResult],
        error_budget_result: Optional[ErrorBudgetResult],
        anomalies: List[Anomaly],
        deployment_identity: str = "dep-568-prod-001",
    ) -> List[Alert]:
        now_iso = datetime.now(timezone.utc).isoformat()
        alerts: List[Alert] = []

        # 1. SLO Breaches & Warnings
        for slo_res in slo_results:
            if slo_res.status == SLOStatus.BREACHED:
                alerts.append(
                    Alert(
                        alert_id=f"alert-{uuid.uuid4().hex[:8]}",
                        source="SLO_ENGINE",
                        alert_type="SLO_BREACH",
                        service=self.service_name,
                        severity=AlertSeverity.CRITICAL,
                        status=AlertStatus.OPEN,
                        summary=f"SLO BREACH: {slo_res.slo.name} - {slo_res.failure_reason or 'Breached'}",
                        timestamp=now_iso,
                        deployment_identity=deployment_identity,
                        details={"slo_result": slo_res.to_dict()},
                    )
                )
            elif slo_res.status == SLOStatus.AT_RISK:
                alerts.append(
                    Alert(
                        alert_id=f"alert-{uuid.uuid4().hex[:8]}",
                        source="SLO_ENGINE",
                        alert_type="SLO_AT_RISK",
                        service=self.service_name,
                        severity=AlertSeverity.WARNING,
                        status=AlertStatus.OPEN,
                        summary=f"SLO AT RISK: {slo_res.slo.name}",
                        timestamp=now_iso,
                        deployment_identity=deployment_identity,
                        details={"slo_result": slo_res.to_dict()},
                    )
                )

        # 2. Error Budget Exhaustion
        if error_budget_result:
            if error_budget_result.status == ErrorBudgetStatus.EXHAUSTED:
                alerts.append(
                    Alert(
                        alert_id=f"alert-{uuid.uuid4().hex[:8]}",
                        source="ERROR_BUDGET_ENGINE",
                        alert_type="ERROR_BUDGET_EXHAUSTION",
                        service=self.service_name,
                        severity=AlertSeverity.EMERGENCY,
                        status=AlertStatus.OPEN,
                        summary="ERROR BUDGET EXHAUSTED: 100% of error budget consumed",
                        timestamp=now_iso,
                        deployment_identity=deployment_identity,
                        details={"error_budget": error_budget_result.to_dict()},
                    )
                )
            elif error_budget_result.status == ErrorBudgetStatus.CRITICAL:
                alerts.append(
                    Alert(
                        alert_id=f"alert-{uuid.uuid4().hex[:8]}",
                        source="ERROR_BUDGET_ENGINE",
                        alert_type="ERROR_BUDGET_CRITICAL",
                        service=self.service_name,
                        severity=AlertSeverity.CRITICAL,
                        status=AlertStatus.OPEN,
                        summary=f"ERROR BUDGET CRITICAL: {error_budget_result.budget.consumption_percentage}% consumed",
                        timestamp=now_iso,
                        deployment_identity=deployment_identity,
                        details={"error_budget": error_budget_result.to_dict()},
                    )
                )

        # 3. Anomalies
        for anomaly in anomalies:
            sev_map = {
                AnomalySeverity.INFO: AlertSeverity.INFO,
                AnomalySeverity.WARNING: AlertSeverity.WARNING,
                AnomalySeverity.CRITICAL: AlertSeverity.CRITICAL,
                AnomalySeverity.EMERGENCY: AlertSeverity.EMERGENCY,
            }
            alerts.append(
                Alert(
                    alert_id=f"alert-{uuid.uuid4().hex[:8]}",
                    source="ANOMALY_DETECTOR",
                    alert_type=anomaly.anomaly_type.value,
                    service=self.service_name,
                    severity=sev_map.get(anomaly.severity, AlertSeverity.WARNING),
                    status=AlertStatus.OPEN,
                    summary=f"ANOMALY DETECTED: {anomaly.anomaly_type.value} (observed: {anomaly.observed_value}, threshold: {anomaly.threshold})",
                    timestamp=now_iso,
                    deployment_identity=deployment_identity,
                    details=anomaly.to_dict(),
                )
            )

        return alerts


class AlertManager:
    """Manages operational alerts with fingerprint deduplication, grouping, and storm suppression."""

    def __init__(self, base_alert_manager: Optional[BaseAlertManager] = None) -> None:
        self.base_alert_manager = base_alert_manager or BaseAlertManager()
        self._alerts: Dict[str, LegacyAlert] = {}
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
    ) -> LegacyAlert:
        fp = f"{tenant_id}:{source_component}:{rule_name}:{resource_id or 'none'}"

        if fp in self._fingerprints:
            existing_id = self._fingerprints[fp]
            existing_alert = self._alerts[existing_id]
            if existing_alert.status == AlertStatus.ACTIVE:
                existing_alert.deduplication_count += 1
                existing_alert.updated_at = _now()
                logger.info(f"[ALERT MANAGER] Deduplicated alert '{existing_id}' (Count: {existing_alert.deduplication_count})")
                return existing_alert

        alert = LegacyAlert(
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

    def acknowledge_alert(self, alert_id: str) -> LegacyAlert:
        alert = self.get_alert(alert_id)
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.updated_at = _now()
        logger.info(f"[ALERT MANAGER] Acknowledged alert '{alert_id}'")
        return alert

    def resolve_alert(self, alert_id: str) -> LegacyAlert:
        alert = self.get_alert(alert_id)
        alert.status = AlertStatus.RESOLVED
        alert.updated_at = _now()

        if alert.fingerprint in self._fingerprints:
            del self._fingerprints[alert.fingerprint]

        logger.info(f"[ALERT MANAGER] Resolved alert '{alert_id}'")
        return alert

    def get_alert(self, alert_id: str) -> LegacyAlert:
        alert = self._alerts.get(alert_id)
        if not alert:
            raise KeyError(f"Alert '{alert_id}' not found")
        return alert

    def list_alerts(self, tenant_id: Optional[str] = None, status: Optional[AlertStatus] = None) -> List[LegacyAlert]:
        res = list(self._alerts.values())
        if tenant_id:
            res = [a for a in res if a.tenant_id == tenant_id]
        if status:
            res = [a for a in res if a.status == status]
        return res
