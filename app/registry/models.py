from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime
from app.core.database import Base


class ModelRegistration(Base):
    """SQLAlchemy table for persistent Model Registry records."""

    __tablename__ = "model_registrations"

    id = Column(String, primary_key=True)
    provider = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    context_window = Column(Integer, default=128000)
    status = Column(String, default="available", index=True)
    config_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
