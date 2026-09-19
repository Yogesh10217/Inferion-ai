import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    secret: Mapped[str] = mapped_column(String, nullable=False)
    secondary_secret: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    event_types: Mapped[List[str]] = mapped_column(JSON, default=list)
    retry_policy: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    deliveries: Mapped[List["WebhookDelivery"]] = relationship(back_populates="endpoint", cascade="all, delete-orphan")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String, default="1.0")
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    actor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, default="llm-inference-engine")
    correlation_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    request_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    deliveries: Mapped[List["WebhookDelivery"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(
        ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_id: Mapped[str] = mapped_column(
        ForeignKey("webhook_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String, default="pending", index=True)  # pending, success, failed, retrying
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_replay: Mapped[bool] = mapped_column(Boolean, default=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    endpoint: Mapped["WebhookEndpoint"] = relationship(back_populates="deliveries")
    event: Mapped["WebhookEvent"] = relationship(back_populates="deliveries")


class DeadLetterEvent(Base):
    __tablename__ = "dead_letter_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    endpoint_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    replay_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    replayed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
