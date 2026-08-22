"""SQLAlchemy ORM Models for Extension Framework Persistence."""

from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import Column, String, DateTime, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class ExtensionModel(Base):
    __tablename__ = "ext_extensions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ext_{uuid.uuid4().hex[:10]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    organization_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    developer_id: Mapped[str] = mapped_column(String, index=True, default="system")
    identifier: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    extension_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    current_version: Mapped[str] = mapped_column(String, default="1.0.0")
    status: Mapped[str] = mapped_column(String, default="INSTALLED")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    manifest_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ExtensionVersionModel(Base):
    __tablename__ = "ext_extension_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"extver_{uuid.uuid4().hex[:10]}")
    extension_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    version_number: Mapped[str] = mapped_column(String, nullable=False)
    manifest_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    package_checksum_sha256: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
