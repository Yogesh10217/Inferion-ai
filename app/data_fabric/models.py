"""SQLAlchemy ORM Models for Data Fabric Persistence."""

from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import Column, String, DateTime, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class DataSourceModel(Base):
    __tablename__ = "df_data_sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ds_{uuid.uuid4().hex[:10]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    organization_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    source_type: Mapped[str] = mapped_column(String, nullable=False)
    connector_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")

    configuration_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    secret_reference: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Secret ID reference ONLY, NO plain text secrets!

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SyncJobModel(Base):
    __tablename__ = "df_sync_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"sync_{uuid.uuid4().hex[:10]}")
    source_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    idempotency_key: Mapped[str] = mapped_column(String, index=True, nullable=False)
    strategy: Mapped[str] = mapped_column(String, default="FULL")
    status: Mapped[str] = mapped_column(String, default="PENDING")

    checkpoint_cursor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    processed_records: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class DataCatalogEntryModel(Base):
    __tablename__ = "df_catalog_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"cat_{uuid.uuid4().hex[:10]}")
    source_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    classification: Mapped[str] = mapped_column(String, default="INTERNAL")
    quality_score: Mapped[float] = mapped_column(Float, default=100.0)

    assets_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
