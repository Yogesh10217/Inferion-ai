"""
Shared Blackboard Architecture for Team Collaboration
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BlackboardEntry(BaseModel):
    entry_id: str
    author_id: str
    category: str = "observation"  # observation, plan, decision, artifact, note
    key: str
    value: Any
    tenant_id: str = "default_tenant"
    workspace_id: str = "default_workspace"
    team_id: str = "default_team"
    timestamp: float = Field(default_factory=time.time)


class Blackboard:
    """Thread-safe, multi-tenant Blackboard workspace for shared reasoning artifacts and decisions."""

    def __init__(self):
        self._lock = threading.RLock()
        # Key: (tenant_id, workspace_id, team_id, key) -> BlackboardEntry
        self._entries: Dict[Tuple[str, str, str, str], BlackboardEntry] = {}

    def write(
        self,
        key: str,
        value: Any,
        author_id: str,
        tenant_id: str = "default_tenant",
        workspace_id: str = "default_workspace",
        team_id: str = "default_team",
        category: str = "observation",
    ) -> BlackboardEntry:
        with self._lock:
            eid = f"entry_{int(time.time() * 1000)}"
            entry = BlackboardEntry(
                entry_id=eid,
                author_id=author_id,
                category=category,
                key=key,
                value=value,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                team_id=team_id,
            )
            dict_key = (tenant_id, workspace_id, team_id, key)
            self._entries[dict_key] = entry
            logger.debug(f"[BLACKBOARD WRITE] key='{key}' author='{author_id}' (tenant={tenant_id}, team={team_id})")
            return entry

    def read(
        self,
        key: str,
        tenant_id: str = "default_tenant",
        workspace_id: str = "default_workspace",
        team_id: str = "default_team",
    ) -> Optional[BlackboardEntry]:
        with self._lock:
            dict_key = (tenant_id, workspace_id, team_id, key)
            return self._entries.get(dict_key)

    def list_entries(
        self,
        tenant_id: str = "default_tenant",
        workspace_id: str = "default_workspace",
        team_id: str = "default_team",
        category: Optional[str] = None,
    ) -> List[BlackboardEntry]:
        with self._lock:
            results = []
            for (tid, wid, team, k), entry in self._entries.items():
                if tid == tenant_id and wid == workspace_id and team == team_id:
                    if category and entry.category != category:
                        continue
                    results.append(entry)
            return results
