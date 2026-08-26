"""Event Source Registry Subsystem (Phase 5.34)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.event_intelligence.exceptions import EventSourceNotRegisteredException, CrossTenantEventAccessException


class EventSourceType(str, Enum):
    RELIABILITY_PLATFORM = "RELIABILITY_PLATFORM"
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"
    AI_LIFECYCLE_PLATFORM = "AI_LIFECYCLE_PLATFORM"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    ARCHITECTURE_PLATFORM = "ARCHITECTURE_PLATFORM"
    COMPLIANCE_PLATFORM = "COMPLIANCE_PLATFORM"
    PORTFOLIO_PLATFORM = "PORTFOLIO_PLATFORM"
    DECISION_INTELLIGENCE = "DECISION_INTELLIGENCE"
    PLATFORM_OPERATIONS = "PLATFORM_OPERATIONS"
    APPLICATION_PLATFORM = "APPLICATION_PLATFORM"
    DEVELOPER_PLATFORM = "DEVELOPER_PLATFORM"
    FINOPS = "FINOPS"
    INTEGRATIONS = "INTEGRATIONS"
    CUSTOM = "CUSTOM"


class EventSourceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"


class EventSourceCapability(str, Enum):
    PUSH_EVENTS = "PUSH_EVENTS"
    POLL_EVENTS = "POLL_EVENTS"
    CORRELATION_SUPPORT = "CORRELATION_SUPPORT"


class EventSourceDefinition(BaseModel):
    source_id: str = Field(default_factory=lambda: f"src_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    source_type: EventSourceType = EventSourceType.CUSTOM
    status: EventSourceStatus = EventSourceStatus.ACTIVE
    capabilities: List[EventSourceCapability] = Field(default_factory=lambda: [EventSourceCapability.PUSH_EVENTS])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventSourceRegistration(BaseModel):
    registration_id: str = Field(default_factory=lambda: f"srcreg_{uuid.uuid4().hex[:12]}")
    source_definition: EventSourceDefinition


class EventSourceManager:
    """Manages enterprise event sources without duplicating ingestion engines."""

    def __init__(self) -> None:
        self._sources: Dict[str, EventSourceDefinition] = {}

    def register_source(
        self,
        tenant_id: str,
        name: str,
        source_type: EventSourceType = EventSourceType.CUSTOM,
    ) -> EventSourceDefinition:
        def_src = EventSourceDefinition(
            tenant_id=tenant_id,
            name=name,
            source_type=source_type,
        )
        self._sources[def_src.source_id] = def_src
        return def_src

    def get_source(self, source_id: str, tenant_id: str) -> EventSourceDefinition:
        src = self._sources.get(source_id)
        if not src:
            raise EventSourceNotRegisteredException(source_id)
        if tenant_id != "global" and src.tenant_id != "global" and tenant_id != src.tenant_id:
            raise CrossTenantEventAccessException(tenant_id, src.tenant_id)
        return src

    def list_sources(self, tenant_id: str) -> List[EventSourceDefinition]:
        return [s for s in self._sources.values() if s.tenant_id == tenant_id]
