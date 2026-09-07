"""Domain Enums & Metadata Definitions for Unified Intelligence."""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class IntelligenceDomain(str, Enum):
    SECURITY = "SECURITY"
    IDENTITY = "IDENTITY"
    OPERATIONS = "OPERATIONS"
    KNOWLEDGE = "KNOWLEDGE"
    POLICY = "POLICY"
    DATA = "DATA"
    MODEL = "MODEL"
    ACCESS = "ACCESS"
    CONTROL = "CONTROL"
    EVENT = "EVENT"
    DECISION = "DECISION"
    GOVERNANCE = "GOVERNANCE"
    COMPLIANCE = "COMPLIANCE"
    FINOPS = "FINOPS"


class DomainReference(BaseModel):
    domain: IntelligenceDomain
    subsystem_name: str
    is_available: bool = True
    version: str = "1.0.0"


class DomainMetadata(BaseModel):
    domain: IntelligenceDomain
    display_name: str
    description: str
    primary_entities: List[str] = Field(default_factory=list)


class DomainHealth(BaseModel):
    domain: IntelligenceDomain
    status: str = "HEALTHY"  # HEALTHY, DEGRADED, UNREACHABLE
    last_signal_timestamp: Optional[datetime] = None


class DomainCapabilityReference(BaseModel):
    domain: IntelligenceDomain
    capability_name: str
    supported_signal_types: List[str] = Field(default_factory=list)
