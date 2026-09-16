"""SQLAlchemy ORM Models for Marketplace Persistence."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class PublisherModel(Base):
    __tablename__ = "mkt_publishers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"pub_{uuid.uuid4().hex[:10]}")
    developer_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    profile_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    verification_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    reputation_score: Mapped[float] = mapped_column(Float, default=100.0)
    published_items_count: Mapped[int] = mapped_column(Integer, default=0)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class MarketplaceItemModel(Base):
    __tablename__ = "mkt_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"mkt_{uuid.uuid4().hex[:10]}")
    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, index=True, nullable=False)
    publisher_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    manifest_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    rating: Mapped[float] = mapped_column(Float, default=5.0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    price_dollars: Mapped[float] = mapped_column(Float, default=0.0)
    tags_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
