"""SQLAlchemy ORM Models for Application Platform (Phase 5.22 - Component 15)."""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class ApplicationModel(Base):
    __tablename__ = "app_applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"app_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    organization_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    app_type: Mapped[str] = mapped_column(String, default="CUSTOM")
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    current_version_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[str] = mapped_column(String, default="system")
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ApplicationVersionModel(Base):
    __tablename__ = "app_application_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"appver_{uuid.uuid4().hex[:12]}")
    application_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    version_fingerprint: Mapped[str] = mapped_column(String, nullable=False)
    configuration_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    composition_references: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_by: Mapped[str] = mapped_column(String, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ApplicationConfigurationModel(Base):
    __tablename__ = "app_application_configurations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"cfg_{uuid.uuid4().hex[:12]}")
    application_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    environment: Mapped[str] = mapped_column(String, default="PRODUCTION")
    feature_overrides: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    model_overrides: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    secret_references: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    runtime_limits: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_by: Mapped[str] = mapped_column(String, default="system")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ApplicationExecutionModel(Base):
    __tablename__ = "app_application_executions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    application_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    application_version_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    trace_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    state: Mapped[str] = mapped_column(String, default="CREATED")
    input_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    cost_attributed_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class InteractionModel(Base):
    __tablename__ = "app_interactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"int_{uuid.uuid4().hex[:12]}")
    conversation_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    interaction_type: Mapped[str] = mapped_column(String, default="CHAT")
    sanitized_input: Mapped[str] = mapped_column(Text, nullable=False)
    sanitized_response: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class FeatureFlagModel(Base):
    __tablename__ = "app_feature_flags"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ff_{uuid.uuid4().hex[:12]}")
    feature_key: Mapped[str] = mapped_column(String, index=True, nullable=False)
    application_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    state: Mapped[str] = mapped_column(String, default="DISABLED")
    targeting_rule: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    experiment_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class PersonalizationProfileModel(Base):
    __tablename__ = "app_personalization_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"prof_{uuid.uuid4().hex[:12]}")
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    consents: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ApplicationFeedbackModel(Base):
    __tablename__ = "app_application_feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"fb_{uuid.uuid4().hex[:12]}")
    application_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    execution_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    feedback_type: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class HumanEscalationModel(Base):
    __tablename__ = "app_human_escalations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"esc_{uuid.uuid4().hex[:12]}")
    application_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    execution_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
