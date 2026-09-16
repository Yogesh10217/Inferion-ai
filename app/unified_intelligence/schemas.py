"""
Pydantic API Schemas for Phase 5.51 Enterprise AI Unified Intelligence.

Defines request/response payload validation schemas separate from domain entities and ORM models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IngestSignalRequestSchema(BaseModel):
    """API request schema for ingesting a domain signal."""
    tenant_id: str = Field(..., description="Tenant identifier")
    domain: str = Field(..., description="Intelligence domain name")
    entity_reference: str = Field(..., description="Reference ID or URI of target entity")
    signal_type: str = Field(..., description="Type of domain signal")
    severity: str = Field(default="MEDIUM", description="Severity level")
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    risk_score: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_references: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = Field(default=None)


class UnifiedSignalResponseSchema(BaseModel):
    """API response schema for unified signal."""
    signal_id: str
    tenant_id: str
    domain: str
    entity_reference: str
    signal_type: str
    severity: str
    confidence_score: float
    risk_score: float
    correlation_id: str
    created_at: datetime


class EnterpriseSituationResponseSchema(BaseModel):
    """API response schema for enterprise situations."""
    situation_id: str
    tenant_id: str
    title: str
    description: str
    status: str
    severity: str
    correlation_id: str
    participating_domains: List[str]
    affected_entities: List[str]
    confidence_score: float
    created_at: datetime
    updated_at: datetime


class EvaluateSituationRequestSchema(BaseModel):
    """API request schema for evaluating enterprise situations."""
    tenant_id: str
    max_signals: int = 100
    max_domains: int = 8
    force_refresh: bool = False
