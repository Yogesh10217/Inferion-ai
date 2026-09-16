"""Enterprise Organizational Memory Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class MemoryType(str, Enum):
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    INSTITUTIONAL = "INSTITUTIONAL"
    DECISION_MEMORY = "DECISION_MEMORY"
    INCIDENT_MEMORY = "INCIDENT_MEMORY"
    OPERATIONAL_MEMORY = "OPERATIONAL_MEMORY"


class MemoryScope(str, Enum):
    REQUEST = "REQUEST"
    SESSION = "SESSION"
    WORKFLOW = "WORKFLOW"
    AGENT = "AGENT"
    APPLICATION = "APPLICATION"
    ENTERPRISE = "ENTERPRISE"


class MemoryRetentionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"


class MemoryReference(BaseModel):
    source_system: str = "KnowledgeIntelligence"
    reference_id: str


class OrganizationalMemory(BaseModel):
    memory_id: str = Field(default_factory=lambda: f"omem_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    memory_type: MemoryType = MemoryType.LONG_TERM
    scope: MemoryScope = MemoryScope.ENTERPRISE
    retention_status: MemoryRetentionStatus = MemoryRetentionStatus.ACTIVE
    key: str
    value_summary: str
    reference: MemoryReference
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrganizationalMemoryManager:
    """Manages tenant-isolated enterprise organizational memory references with retention governance."""

    def __init__(self) -> None:
        self._memories: Dict[str, OrganizationalMemory] = {}

    def record_memory(
        self,
        tenant_id: str,
        key: str,
        value_summary: str,
        memory_type: MemoryType = MemoryType.LONG_TERM,
        scope: MemoryScope = MemoryScope.ENTERPRISE,
        reference_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OrganizationalMemory:
        sanitized_meta = SensitiveDataSanitizer.sanitize(metadata or {})
        ref = MemoryReference(reference_id=reference_id or uuid.uuid4().hex[:8])
        mem = OrganizationalMemory(
            tenant_id=tenant_id,
            memory_type=memory_type,
            scope=scope,
            key=key,
            value_summary=value_summary,
            reference=ref,
            metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
        )
        self._memories[mem.memory_id] = mem
        return mem

    def list_memories(self, tenant_id: str, scope: Optional[MemoryScope] = None) -> List[OrganizationalMemory]:
        results = [m for m in self._memories.values() if m.tenant_id == tenant_id]
        if scope:
            results = [m for m in results if m.scope == scope]
        return results
