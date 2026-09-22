from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ModelRegistration(Base):
    """SQLAlchemy table for persistent Model Registry records."""

    __tablename__ = "model_registrations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    context_window: Mapped[Optional[int]] = mapped_column(Integer, default=128000)
    status: Mapped[Optional[str]] = mapped_column(String, default="available", index=True)
    config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
