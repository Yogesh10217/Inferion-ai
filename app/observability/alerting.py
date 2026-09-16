"""Enterprise Alerting Platform with event bus integration and notification channel adapters."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from app.observability.context import ObservabilityContext, get_current_context
from app.observability.exceptions import AlertConfigurationException

logger = logging.getLogger(__name__)


class NotificationChannel(Protocol):
    """Protocol interface for alerting notification channels (Webhook, Slack, Email, PagerDuty)."""

    async def send_notification(self, alert_data: Dict[str, Any]) -> bool:
        ...


class ConsoleNotificationChannel:
    """Default notification channel emitting alert logs."""

    async def send_notification(self, alert_data: Dict[str, Any]) -> bool:
        logger.warning(f"🚨 [ALERT {alert_data['level']}] {alert_data['title']}: {alert_data['message']}")
        return True


@dataclass
class Alert:
    """Represents an active or historical system alert."""
    alert_id: str
    title: str
    condition_type: str  # CRITICAL_FAILURE, SLA_VIOLATION, COST_SPIKE, BUDGET_THRESHOLD, HIGH_ERROR_RATE, AGENT_STUCK, WORKFLOW_STUCK, EXECUTION_LOOP, TOOL_FAILURE, PROVIDER_OUTAGE
    level: str  # INFO, WARNING, CRITICAL
    status: str  # FIRING, ACKNOWLEDGED, RESOLVED
    message: str
    tenant_id: str = "default"
    workspace_id: str = "default"
    organization_id: str = "default"
    execution_id: Optional[str] = None
    component: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    acknowledged_at: Optional[float] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AlertManager:
    """Manages creation, trigger evaluation, state transitions, and channel notifications for system alerts."""

    def __init__(self, event_bus: Optional[Any] = None) -> None:
        self.event_bus = event_bus
        self._alerts: Dict[str, Alert] = {}
        self._notification_channels: List[NotificationChannel] = [ConsoleNotificationChannel()]

    def register_channel(self, channel: NotificationChannel) -> None:
        """Register a notification channel adapter."""
        self._notification_channels.append(channel)

    def create_alert(
        self,
        title: str,
        condition_type: str,
        level: str,
        message: str,
        component: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        context: Optional[ObservabilityContext] = None,
    ) -> Alert:
        """Create and register an alert record."""
        if level.upper() not in ["INFO", "WARNING", "CRITICAL"]:
            raise AlertConfigurationException(f"Invalid alert level '{level}'. Allowed: INFO, WARNING, CRITICAL")

        ctx = context or get_current_context()
        alert_id = f"alert-{int(time.time() * 1000)}-{len(self._alerts) + 1}"

        alert = Alert(
            alert_id=alert_id,
            title=title,
            condition_type=condition_type,
            level=level.upper(),
            status="FIRING",
            message=message,
            tenant_id=ctx.tenant_id or "default",
            workspace_id=ctx.workspace_id or "default",
            organization_id=ctx.organization_id or "default",
            execution_id=ctx.execution_id,
            component=component,
            attributes=attributes or {},
        )

        self._alerts[alert_id] = alert
        return alert

    async def trigger_alert(
        self,
        title: str,
        condition_type: str,
        level: str,
        message: str,
        component: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        context: Optional[ObservabilityContext] = None,
    ) -> Alert:
        """Create an alert, dispatch via event bus and notify configured channels."""
        alert = self.create_alert(title, condition_type, level, message, component, attributes, context)
        alert_data = alert.to_dict()

        # Publish to Event Bus if available
        if self.event_bus and hasattr(self.event_bus, "publish"):
            try:
                await self.event_bus.publish("observability.alert.triggered", payload=alert_data)
            except Exception as e:
                logger.error(f"Failed to publish alert to event bus: {e}")

        # Send via notification channels
        for channel in self._notification_channels:
            try:
                await channel.send_notification(alert_data)
            except Exception as e:
                logger.error(f"Notification channel failed: {e}")

        return alert

    def acknowledge_alert(self, alert_id: str, user_id: str = "system") -> Alert:
        """Acknowledge an active alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            raise AlertConfigurationException(f"Alert with ID '{alert_id}' not found.")

        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = time.time()
        alert.acknowledged_by = user_id
        return alert

    def resolve_alert(self, alert_id: str) -> Alert:
        """Resolve an active or acknowledged alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            raise AlertConfigurationException(f"Alert with ID '{alert_id}' not found.")

        alert.status = "RESOLVED"
        alert.resolved_at = time.time()
        return alert

    def evaluate_alert(
        self,
        metric_name: str,
        current_value: float,
        threshold: float,
        condition_type: str,
        title: str,
        component: str,
    ) -> Optional[Alert]:
        """Evaluate a metric against a threshold and trigger an alert if broken."""
        if current_value >= threshold:
            return self.create_alert(
                title=title,
                condition_type=condition_type,
                level="CRITICAL" if current_value > threshold * 1.5 else "WARNING",
                message=f"Alert rule evaluated broken for {metric_name} in {component}: current {current_value} >= threshold {threshold}.",
                component=component,
            )
        return None

    def get_alerts(
        self,
        status: Optional[str] = None,
        level: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve alerts matching filter parameters."""
        alerts = list(self._alerts.values())
        if status:
            alerts = [a for a in alerts if a.status.upper() == status.upper()]
        if level:
            alerts = [a for a in alerts if a.level.upper() == level.upper()]
        if tenant_id:
            alerts = [a for a in alerts if a.tenant_id == tenant_id]

        return [a.to_dict() for a in alerts]
