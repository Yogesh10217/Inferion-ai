from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AIAssetModel(Base):
    """SQLAlchemy model for persistent AI Assets."""

    __tablename__ = "ai_assets"

    asset_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, default="global", index=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="")

    current_version: Mapped[str] = mapped_column(String, default="1.0.0")
    status: Mapped[str] = mapped_column(String, default="DRAFT", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    versions: Mapped[List["AIAssetVersionModel"]] = relationship(
        "AIAssetVersionModel", back_populates="asset", cascade="all, delete-orphan", lazy="selectin"
    )


class AIAssetVersionModel(Base):
    """SQLAlchemy model for persistent immutable AI Asset Versions."""

    __tablename__ = "ai_asset_versions"

    version_id: Mapped[str] = mapped_column(String, primary_key=True)
    version_number: Mapped[str] = mapped_column(String, nullable=False)
    asset_id: Mapped[str] = mapped_column(
        String, ForeignKey("ai_assets.asset_id", ondelete="CASCADE"), nullable=False, index=True
    )

    tenant_id: Mapped[str] = mapped_column(String, default="global")
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    creator: Mapped[str] = mapped_column(String, default="system")
    configuration_json: Mapped[str] = mapped_column(Text, default="{}")
    configuration_hash: Mapped[str] = mapped_column(String, default="")
    dependencies_json: Mapped[str] = mapped_column(Text, default="{}")
    parent_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    changelog: Mapped[str] = mapped_column(Text, default="")

    status: Mapped[str] = mapped_column(String, default="DRAFT")
    approval_status: Mapped[str] = mapped_column(String, default="NOT_REQUESTED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=False)

    asset: Mapped[Optional["AIAssetModel"]] = relationship("AIAssetModel", back_populates="versions")

    __table_args__ = (Index("idx_asset_version_num", "asset_id", "version_number", unique=True),)
