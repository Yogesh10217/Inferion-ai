"""SQLAlchemy ORM Models for Developer Platform Persistence."""

from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import Column, String, DateTime, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class DeveloperModel(Base):
    __tablename__ = "dp_developers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"dev_{uuid.uuid4().hex[:10]}")
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    status: Mapped[str] = mapped_column(String, default="PENDING")
    profile_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    permissions_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class DeveloperProjectModel(Base):
    __tablename__ = "dp_projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"proj_{uuid.uuid4().hex[:10]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    workspace_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    developer_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    version: Mapped[str] = mapped_column(String, default="0.1.0")
    lifecycle: Mapped[str] = mapped_column(String, default="CREATED")
    repository_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    runtime_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class WebhookSubscriptionModel(Base):
    __tablename__ = "dp_webhook_subscriptions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"sub_{uuid.uuid4().hex[:10]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    developer_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_url: Mapped[str] = mapped_column(String, nullable=False)
    secret_key: Mapped[str] = mapped_column(String, nullable=False)
    event_types: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_retries: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
