"""SQLAlchemy Persistence Models for Integration Platform Subsystems."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, String

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntegrationModel(Base):
    __tablename__ = "integ_integrations"

    integration_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(64), nullable=False, default="SAAS", index=True)
    status = Column(String(64), nullable=False, default="ACTIVE", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)

    credential_id = Column(String(64), nullable=True)
    health_status = Column(String(64), nullable=False, default="HEALTHY")
    config_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)


class WebhookEndpointModel(Base):
    __tablename__ = "integ_webhook_endpoints"

    endpoint_id = Column(String(64), primary_key=True, index=True)
    url = Column(String(1024), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=_now)


class AutomationModel(Base):
    __tablename__ = "integ_automations"

    automation_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    trigger_type = Column(String(64), nullable=False, default="WEBHOOK")
    action_type = Column(String(64), nullable=False, default="CALL_API")
    tenant_id = Column(String(64), nullable=False, index=True)

    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=_now)


class PluginModel(Base):
    __tablename__ = "integ_plugins"

    plugin_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(64), nullable=False, default="ACTIVE")
    tenant_id = Column(String(64), nullable=False, index=True)

    manifest_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
