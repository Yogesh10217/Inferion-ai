"""
Memory Database Persistence Models (SQLAlchemy)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, Index, String, Text

from app.core.database import Base


class MemoryRecordModel(Base):
    __tablename__ = "memory_records"

    id = Column(String(64), primary_key=True, default=lambda: f"mem_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    user_id = Column(String(64), nullable=True, index=True)
    memory_type = Column(String(32), nullable=False, index=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=1.0)
    importance_score = Column(Float, default=0.5)
    retention_policy = Column(String(32), default="PERMANENT")
    status = Column(String(32), default="ACTIVE")
    embedding_id = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True, index=True)

    __table_args__ = (
        Index("idx_mem_org_ws", "organization_id", "workspace_id"),
        Index("idx_mem_user_type", "user_id", "memory_type"),
    )


class ConversationMemoryModel(Base):
    __tablename__ = "conversation_memories"

    id = Column(String(64), primary_key=True, default=lambda: f"conv_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=True)
    messages_json = Column(JSON, nullable=False)
    summary = Column(Text, nullable=True)
    token_count = Column(Float, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SemanticMemoryModel(Base):
    __tablename__ = "semantic_memories"

    id = Column(String(64), primary_key=True, default=lambda: f"sem_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    fact = Column(Text, nullable=False)
    category = Column(String(64), default="general")
    confidence_score = Column(Float, default=1.0)
    importance_score = Column(Float, default=0.5)
    embedding_id = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ProfileMemoryModel(Base):
    __tablename__ = "profile_memories"

    id = Column(String(64), primary_key=True, default=lambda: f"prof_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    user_id = Column(String(64), nullable=False, index=True, unique=True)
    profile_data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SessionMemoryModel(Base):
    __tablename__ = "session_memories"

    id = Column(String(64), primary_key=True, default=lambda: f"sess_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    context_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True, index=True)


class EpisodicMemoryModel(Base):
    __tablename__ = "episodic_memories"

    id = Column(String(64), primary_key=True, default=lambda: f"ep_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    episode_type = Column(String(64), nullable=False)
    source_id = Column(String(64), nullable=False)
    summary = Column(Text, nullable=False)
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
