"""
Unified Memory Storage Engine & Repository Implementation
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.memory.exceptions import MemoryNotFoundError, TenantMemoryIsolationError
from app.memory.memory_types import MemoryStatus, MemoryType, RetentionPolicy


class MemoryItemRecord:
    def __init__(
        self,
        organization_id: str,
        workspace_id: str,
        memory_type: MemoryType,
        content: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        importance_score: float = 0.5,
        confidence_score: float = 1.0,
        retention_policy: RetentionPolicy = RetentionPolicy.PERMANENT,
        memory_id: Optional[str] = None,
    ):
        self.memory_id = memory_id or f"mem_{uuid.uuid4().hex[:12]}"
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.memory_type = memory_type
        self.content = content
        self.metadata = metadata or {}
        self.importance_score = importance_score
        self.confidence_score = confidence_score
        self.retention_policy = retention_policy
        self.status = MemoryStatus.ACTIVE
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.expires_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.memory_id,
            "organization_id": self.organization_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "memory_type": self.memory_type.value if isinstance(self.memory_type, MemoryType) else str(self.memory_type),
            "content": self.content,
            "metadata": self.metadata,
            "importance_score": self.importance_score,
            "confidence_score": self.confidence_score,
            "retention_policy": self.retention_policy.value if isinstance(self.retention_policy, RetentionPolicy) else str(self.retention_policy),
            "status": self.status.value if isinstance(self.status, MemoryStatus) else str(self.status),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
        }


class MemoryStore:
    """Unified Memory Storage Engine providing CRUD, tenant isolation, and status filtering."""

    def __init__(self):
        self._records: Dict[str, MemoryItemRecord] = {}

    def save(self, record: MemoryItemRecord) -> MemoryItemRecord:
        if not record.organization_id:
            raise TenantMemoryIsolationError("organization_id required to save memory record")
        self._records[record.memory_id] = record
        return record

    def get(self, memory_id: str, organization_id: str) -> MemoryItemRecord:
        if memory_id not in self._records:
            raise MemoryNotFoundError(f"Memory record '{memory_id}' not found")
        rec = self._records[memory_id]
        if rec.organization_id != organization_id:
            raise TenantMemoryIsolationError(f"Tenant isolation mismatch for memory record '{memory_id}'")
        return rec

    def update(self, memory_id: str, organization_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> MemoryItemRecord:
        rec = self.get(memory_id, organization_id)
        if content:
            rec.content = content
        if metadata:
            rec.metadata.update(metadata)
        rec.updated_at = datetime.now(timezone.utc).isoformat()
        return rec

    def delete(self, memory_id: str, organization_id: str) -> bool:
        rec = self.get(memory_id, organization_id)
        rec.status = MemoryStatus.DELETED
        return True

    def archive(self, memory_id: str, organization_id: str) -> MemoryItemRecord:
        rec = self.get(memory_id, organization_id)
        rec.status = MemoryStatus.ARCHIVED
        return rec

    def list(self, organization_id: str, workspace_id: Optional[str] = None, memory_type: Optional[str] = None) -> List[MemoryItemRecord]:
        results = []
        for rec in self._records.values():
            if rec.organization_id != organization_id:
                continue
            if workspace_id and rec.workspace_id != workspace_id:
                continue
            if memory_type and (rec.memory_type.value if isinstance(rec.memory_type, MemoryType) else str(rec.memory_type)) != memory_type:
                continue
            if rec.status == MemoryStatus.ACTIVE:
                results.append(rec)
        return results

    def search(self, query: str, organization_id: str, top_k: int = 10) -> List[MemoryItemRecord]:
        records = self.list(organization_id)
        q_words = set(query.lower().split())

        def match_fn(rec: MemoryItemRecord) -> int:
            words = set(rec.content.lower().split())
            return len(q_words.intersection(words))

        records.sort(key=match_fn, reverse=True)
        return records[:top_k]

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "total_records": len(self._records)}
