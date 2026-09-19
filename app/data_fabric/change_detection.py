"""Change Data Capture (CDC) & Event Detection Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ChangeType(str, Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    MOVED = "MOVED"
    RENAMED = "RENAMED"
    SCHEMA_CHANGED = "SCHEMA_CHANGED"
    PERMISSION_CHANGED = "PERMISSION_CHANGED"


class ChangeEvent(BaseModel):
    """Event capturing data mutation or schema change."""

    event_id: str = Field(default_factory=lambda: f"cdc_{uuid.uuid4().hex[:10]}")
    source_id: str
    tenant_id: str = "global"
    change_type: ChangeType
    record_id: Optional[str] = None
    table_or_resource: Optional[str] = None
    changes: Dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=_now)


class ChangeDetector:
    """Detects mutations and dispatches events to Knowledge/RAG, Cache, Workflows, and Agents."""

    def __init__(self) -> None:
        self._events: List[ChangeEvent] = []
        self._handlers: List[Any] = []

    def record_change(
        self,
        source_id: str,
        change_type: ChangeType,
        tenant_id: str = "global",
        record_id: Optional[str] = None,
        table_or_resource: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> ChangeEvent:
        """Create and publish change event."""
        evt = ChangeEvent(
            source_id=source_id,
            tenant_id=tenant_id,
            change_type=change_type,
            record_id=record_id,
            table_or_resource=table_or_resource,
            changes=changes or {},
        )
        self._events.append(evt)
        logger.info(
            f"[CHANGE DETECTOR] Detected change '{change_type.value}' on source '{source_id}' (Record: {record_id})"
        )

        # Notify registered change listeners
        for handler in self._handlers:
            try:
                handler(evt)
            except Exception as e:
                logger.error(f"[CHANGE DETECTOR HANDLER ERROR] Listener failed: {e}")

        return evt

    def register_listener(self, handler: Any) -> None:
        self._handlers.append(handler)

    def list_events(self, source_id: Optional[str] = None, tenant_id: Optional[str] = None) -> List[ChangeEvent]:
        res = list(self._events)
        if source_id:
            res = [e for e in res if e.source_id == source_id]
        if tenant_id:
            res = [e for e in res if e.tenant_id == tenant_id]
        return res
