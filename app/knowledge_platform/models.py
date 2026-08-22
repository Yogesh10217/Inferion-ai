"""SQLAlchemy Persistence Models for Knowledge Platform Subsystems."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeItemModel(Base):
    __tablename__ = "kp_knowledge_items"

    item_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    knowledge_type = Column(String(64), nullable=False, default="DOCUMENT", index=True)
    status = Column(String(64), nullable=False, default="ACTIVE", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)

    source_id = Column(String(64), nullable=False, default="src_default")
    confidence_score = Column(Float, nullable=False, default=1.0)
    classification = Column(String(64), nullable=False, default="INTERNAL")

    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)


class MemoryModel(Base):
    __tablename__ = "kp_memories"

    memory_id = Column(String(64), primary_key=True, index=True)
    key = Column(String(255), nullable=False, index=True)
    memory_type = Column(String(64), nullable=False, default="ORGANIZATIONAL", index=True)
    scope = Column(String(64), nullable=False, default="TENANT", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)

    owner_agent_id = Column(String(64), nullable=True, index=True)
    confidence_score = Column(Float, nullable=False, default=1.0)
    value_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)


class KnowledgeGraphNodeModel(Base):
    __tablename__ = "kp_graph_nodes"

    node_id = Column(String(64), primary_key=True, index=True)
    label = Column(String(255), nullable=False, index=True)
    node_type = Column(String(64), nullable=False, default="ENTITY", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    properties_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=_now)


class KnowledgeGraphEdgeModel(Base):
    __tablename__ = "kp_graph_edges"

    edge_id = Column(String(64), primary_key=True, index=True)
    source_node_id = Column(String(64), nullable=False, index=True)
    target_node_id = Column(String(64), nullable=False, index=True)
    relationship = Column(String(64), nullable=False, default="RELATED_TO", index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    weight = Column(Float, nullable=False, default=1.0)

    created_at = Column(DateTime, nullable=False, default=_now)
