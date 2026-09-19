import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class KnowledgeBase(Base):
    """
    Represents a collection of knowledge documents.
    Multi-tenant aware via workspace_id and organization_id.
    """

    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    documents: Mapped[List["KnowledgeDocument"]] = relationship(
        back_populates="knowledge_base", cascade="all, delete-orphan"
    )
    jobs: Mapped[List["IndexJob"]] = relationship(back_populates="knowledge_base", cascade="all, delete-orphan")


class KnowledgeDocument(Base):
    """
    Represents a single document in a knowledge base, supporting versioning and soft-deletes.
    """

    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_base_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    content_uri: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Soft delete & lifecycle
    status: Mapped[str] = mapped_column(String, default="ACTIVE", index=True)  # ACTIVE, ARCHIVED, PURGED
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    purged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    purged_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    knowledge_base: Mapped["KnowledgeBase"] = relationship(back_populates="documents")
    chunks: Mapped[List["KnowledgeChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    """
    Represents a chunk of text extracted from a KnowledgeDocument.
    """

    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"), index=True, nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    start_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_heading: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    parent_chunk: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")
    embedding_records: Mapped[List["EmbeddingRecord"]] = relationship(
        back_populates="chunk", cascade="all, delete-orphan"
    )


class EmbeddingRecord(Base):
    """
    Stores the vector embedding for a KnowledgeChunk.
    """

    __tablename__ = "embedding_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), index=True, nullable=False
    )

    model_name: Mapped[str] = mapped_column(String, nullable=False)
    vector: Mapped[Any] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    chunk: Mapped["KnowledgeChunk"] = relationship(back_populates="embedding_records")


class RetrievalSession(Base):
    """
    Tracks a retrieval session/query to link citations.
    """

    __tablename__ = "retrieval_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    citations: Mapped[List["Citation"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Citation(Base):
    """
    Links a chunk to a retrieval session, indicating it was cited.
    """

    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(
        ForeignKey("retrieval_sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chunk_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), index=True, nullable=False
    )

    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["RetrievalSession"] = relationship(back_populates="citations")


class IndexJob(Base):
    """
    Tracks the asynchronous status of a document indexing process.
    """

    __tablename__ = "index_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_base_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"), index=True, nullable=False
    )

    status: Mapped[str] = mapped_column(String, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    knowledge_base: Mapped["KnowledgeBase"] = relationship(back_populates="jobs")
