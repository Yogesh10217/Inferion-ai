"""
SQLAlchemy / ORM Database Models for Phase 5.51 Enterprise AI Unified Intelligence.

Defines persistence model structures for database serialization.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class UnifiedSignalORM(BaseModel):
    """ORM representation of unified signals."""
    signal_id: str
    tenant_id: str
    domain: str
    entity_reference: str
    signal_type: str
    severity: str
    confidence_score: float
    risk_score: float
    correlation_id: str
    metadata_json: str = "{}"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EnterpriseSituationORM(BaseModel):
    """ORM representation of enterprise situations."""
    situation_id: str
    tenant_id: str
    title: str
    description: str
    status: str
    severity: str
    correlation_id: str
    confidence_score: float
    participating_domains_json: str = "[]"
    affected_entities_json: str = "[]"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
