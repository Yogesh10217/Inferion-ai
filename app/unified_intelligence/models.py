"""
Domain Entity Data Models for Phase 5.51 Enterprise AI Unified Intelligence.

Defines internal domain entities separate from API schemas and SQLAlchemy ORM models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.situation_awareness import SituationSeverity, SituationStatus


@dataclass
class DomainSignalEntity:
    """Internal domain signal model."""
    signal_id: str
    tenant_id: str
    domain: IntelligenceDomain
    entity_reference: str
    signal_type: str
    severity: str
    confidence_score: float
    risk_score: float
    correlation_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EnterpriseSituationEntity:
    """Internal enterprise situation model."""
    situation_id: str
    tenant_id: str
    title: str
    description: str
    status: SituationStatus
    severity: SituationSeverity
    correlation_id: str
    participating_domains: List[IntelligenceDomain] = field(default_factory=list)
    affected_entities: List[str] = field(default_factory=list)
    confidence_score: float = 0.85
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
